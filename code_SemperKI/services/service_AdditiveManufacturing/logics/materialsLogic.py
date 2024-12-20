"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the materials
"""
import logging, numpy
from datetime import datetime

from django.utils import timezone

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.connections.redis import RedisConnection

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import ProcessUpdates
from code_SemperKI.handlers.public.process import updateProcessFunction
from code_SemperKI.services.service_AdditiveManufacturing.definitions import ServiceDetails, MaterialDetails
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks

from ..definitions import NodeTypesAM, NodePropertiesAMMaterial

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################

##################################################
def logicForRetrieveMaterialWithFilter(filters) -> tuple[dict|Exception, int]:

    try:
        # format:
        # "filters":[ {"id":0,
        #          "isChecked":False,
        #          "isOpen":False,
        #          "question":{
        #              "isSelectable":True,
        #              "title":"materialCategory",
        #              "category":"MATERIAL",
        #              "type":"SELECTION",
        #              "range":None,
        #              "values":[{"name": <nodeName>, "id": <nodeID>}, ...],
        #              "units":None
        #              },
        #         "answer":None
        #         },...
        # ]
        output = {"materials": []}
        
        #filtersForSparql = []
        #for entry in filters["filters"]:
        #    filtersForSparql.append([entry["question"]["title"], entry["answer"]])
        #TODO ask via sparql with most general filter and then iteratively filter response
        #resultsOfQueries = {"materials": []}
        #materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        # for elem in materialsRes:
        #     title = elem["Material"]["value"]
        #     resultsOfQueries["materials"].append({"id": crypto.generateMD5(title), "title": title, "propList": [], "imgPath": mocks.testPicture})

        # TODO filter by selection of post-processing

        # calculate median price if not found in redis or date is too old
        redisConn = RedisConnection()
        if redisConn.retrieveContentJSON("medianMaterialPrices")[1] == False or redisConn.retrieveContent("medianMaterialPricesDate")[1] == False or (timezone.now() - datetime.fromisoformat(redisConn.retrieveContent("medianMaterialPricesDate")[0])).days > 1:
            materialPrices = {}
            listOfAllMaterialNodes = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
            for materialNode in listOfAllMaterialNodes:
                if materialNode[pgKnowledgeGraph.NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                    for propertyValue in materialNode[pgKnowledgeGraph.NodeDescription.properties]:
                        if NodePropertiesAMMaterial.acquisitionCosts == propertyValue[pgKnowledgeGraph.NodePropertyDescription.name]:
                            if materialNode[pgKnowledgeGraph.NodeDescription.uniqueID] in materialPrices:
                                materialPrices[materialNode[pgKnowledgeGraph.NodeDescription.uniqueID]].append(float(propertyValue[pgKnowledgeGraph.NodePropertyDescription.value]))
                            else:
                                materialPrices[materialNode[pgKnowledgeGraph.NodeDescription.uniqueID]] = [float(propertyValue[pgKnowledgeGraph.NodePropertyDescription.value])]
                
            for key in materialPrices:
                materialPrices[key] = numpy.median(materialPrices[key])
            redisConn.addContentJSON("medianMaterialPrices", materialPrices)
            redisConn.addContent("medianMaterialPricesDate", timezone.now().isoformat())
        # else: take value from redis
        else:
            materialPrices = redisConn.retrieveContentJSON("medianMaterialPrices")[0]

        materialList = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
        for entry in materialList:
            # use only entries from system
            if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner: #and entry[pgKnowledgeGraph.NodeDescription.active] == True:
                # adhere to the filters:
                append = True
                for filter in filters["filters"]:
                    # see if filter is selected and the value has not been rules out somewhere
                    if filter["isChecked"] == True and append == True:
                        # filter for material category
                        if filter["question"]["title"] == "materialCategory":
                            appendViaThisFilter = False
                            if filter["answer"] != None:
                                categoryID = filter["answer"]["value"] # contains the id of the chosen category node
                                categoriesOfEntry = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(entry[pgKnowledgeGraph.NodeDescription.uniqueID], NodeTypesAM.materialCategory)
                                if isinstance(categoriesOfEntry, Exception):
                                    raise categoriesOfEntry

                                for category in categoriesOfEntry:
                                    if categoryID == category[pgKnowledgeGraph.NodeDescription.uniqueID]:
                                        appendViaThisFilter = True
                                        break
                            append = appendViaThisFilter

                if append:
                    imgPath = entry[pgKnowledgeGraph.NodeDescription.properties][NodePropertiesAMMaterial.imgPath] if NodePropertiesAMMaterial.imgPath in entry[pgKnowledgeGraph.NodeDescription.properties] else mocks.testPicture
                    output["materials"].append({"id": entry[pgKnowledgeGraph.NodeDescription.nodeID], "title": entry[pgKnowledgeGraph.NodeDescription.nodeName], "propList": entry[pgKnowledgeGraph.NodeDescription.properties], "imgPath": imgPath, "medianPrice": materialPrices[entry[pgKnowledgeGraph.NodeDescription.uniqueID]] if entry[pgKnowledgeGraph.NodeDescription.uniqueID] in materialPrices else 0.})

        # mockup here:
        #mock = copy.deepcopy(mocks.materialMock)
        #mock["materials"].extend(resultsOfQueries["materials"])
        #output.update(mock)
        return (output, 200)
    except Exception as e:
        return (e, 500)

##################################################
def logicForSetMaterial(request, projectID, processID, groupIndex, material, functionName) -> tuple[dict|Exception, int]:
    """
    Set a material

    :param request: The request
    :type request: Request
    :return: The material or Exception and status code
    :rtype: dict|Exception, int
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return (Exception(f"Rights not sufficient in {functionName}"), 401)

        materialToBeSaved = {}
        materialToBeSaved[material[MaterialDetails.id]] = material

        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupIndex] = {ServiceDetails.material: materialToBeSaved}
        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: updateArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            return (Exception(f"Rights not sufficient for {functionName}"), 401)
            
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},set,{Logging.Object.OBJECT},material,"+str(datetime.now()))
        
        return (None, 200)
    except Exception as e:
        return (e, 500)