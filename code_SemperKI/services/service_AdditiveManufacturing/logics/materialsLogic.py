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
from code_SemperKI.logics.processLogics import updateProcessFunction
from code_SemperKI.modelFiles.processModel import ProcessDescription
from code_SemperKI.modelFiles.projectModel import ProjectDescription
from code_SemperKI.services.service_AdditiveManufacturing.definitions import ServiceDetails, MaterialDetails
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks
from code_SemperKI.utilities.locales import manageTranslations

from ..definitions import SERVICE_NAME, NodeTypesAM, NodePropertiesAMMaterial

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################

##################################################
def logicForRetrieveMaterialWithFilter(filters, locale:str) -> tuple[dict|Exception, int]:

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
        
        # TODO filter by selection of post-processing

        # calculate median price if not found in redis or date is too old
        redisConn = RedisConnection()
        redisContentMedianMaterialPrices = redisConn.retrieveContentJSON("medianMaterialPrices")
        redisContentMedianMaterialPricesDate = redisConn.retrieveContent("medianMaterialPricesDate")
        if redisContentMedianMaterialPrices[1] is False or redisContentMedianMaterialPricesDate[1] is False or (timezone.now() - datetime.fromisoformat(redisContentMedianMaterialPricesDate[0])).days > 1:
            materialPrices = {}
            listOfAllMaterialNodes = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
            for materialNode in listOfAllMaterialNodes:
                if materialNode[pgKnowledgeGraph.NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                    for propertyValue in materialNode[pgKnowledgeGraph.NodeDescription.properties]:
                        if NodePropertiesAMMaterial.acquisitionCosts == propertyValue[pgKnowledgeGraph.NodePropertyDescription.key]:
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
            materialPrices = redisContentMedianMaterialPrices[0]

        materialList = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
        for entry in materialList:
            # use only entries from orgas
            if entry[pgKnowledgeGraph.NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner and entry[pgKnowledgeGraph.NodeDescription.active] is True:
                # adhere to the filters:
                append = True
                for filterEntry in filters["filters"]:
                    # see if filter is selected and the value has not been rules out somewhere
                    if filterEntry["isChecked"] is True and append is True:
                        # filter for material category
                        if filterEntry["question"]["title"] == "materialCategory":
                            appendViaThisFilter = False
                            if filterEntry["answer"] is not None:
                                categoryID = filterEntry["answer"]["value"] # contains the id of the chosen category node
                                categoriesOfEntry = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(entry[pgKnowledgeGraph.NodeDescription.uniqueID], NodeTypesAM.materialCategory)
                                if isinstance(categoriesOfEntry, Exception):
                                    raise categoriesOfEntry

                                for category in categoriesOfEntry:
                                    if categoryID == category[pgKnowledgeGraph.NodeDescription.uniqueID]:
                                        appendViaThisFilter = True
                                        break
                                append = appendViaThisFilter

                        # filter for material tensile strenght
                        if filterEntry["question"]["title"] == "tensileStrength":
                            appendViaThisFilter = False
                            if filterEntry["answer"] is not None:
                                answerRange = [filterEntry["answer"]["value"]["min"], filterEntry["answer"]["value"]["max"]]
                                propertiesOfEntry = entry[pgKnowledgeGraph.NodeDescription.properties]
                                for prop in propertiesOfEntry:
                                    if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.ultimateTensileStrength:
                                        if float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) >= answerRange[0] and float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) <= answerRange[1]:
                                            appendViaThisFilter = True
                                            break

                                append = appendViaThisFilter
                        
                        # filter for material density
                        if filterEntry["question"]["title"] == "density":
                            appendViaThisFilter = False
                            if filterEntry["answer"] is not None:
                                answerRange = [filterEntry["answer"]["value"]["min"], filterEntry["answer"]["value"]["max"]]
                                propertiesOfEntry = entry[pgKnowledgeGraph.NodeDescription.properties]
                                for prop in propertiesOfEntry:
                                    if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.density:
                                        if float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) >= answerRange[0] and float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) <= answerRange[1]:
                                            appendViaThisFilter = True
                                            break

                                append = appendViaThisFilter
                        
                        # filter for material elongation at break
                        if filterEntry["question"]["title"] == "elongationAtBreak":
                            appendViaThisFilter = False
                            if filterEntry["answer"] is not None:
                                answerRange = [filterEntry["answer"]["value"]["min"], filterEntry["answer"]["value"]["max"]]
                                propertiesOfEntry = entry[pgKnowledgeGraph.NodeDescription.properties]
                                for prop in propertiesOfEntry:
                                    if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.elongationAtBreak:
                                        if float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) >= answerRange[0] and float(prop[pgKnowledgeGraph.NodePropertyDescription.value]) <= answerRange[1]:
                                            appendViaThisFilter = True
                                            break

                                append = appendViaThisFilter
                        
                        # filter for material certificates
                        if filterEntry["question"]["title"] == "certificates":
                            appendViaThisFilter = False
                            if filterEntry["answer"] is not None:
                                certificates = filterEntry["answer"]["value"]
                                propertiesOfEntry = entry[pgKnowledgeGraph.NodeDescription.properties]
                                for prop in propertiesOfEntry:
                                    if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.certificates:
                                        propValues = prop[pgKnowledgeGraph.NodePropertyDescription.value].split(",")
                                        for cert in certificates:
                                            if cert in propValues:
                                                appendViaThisFilter = True
                                            else:
                                                appendViaThisFilter = False
                                                break
                                        break

                                append = appendViaThisFilter


                if append:
                    # prepare properties
                    imgPath = mocks.testPicture
                    for propIdx, prop in enumerate(entry[pgKnowledgeGraph.NodeDescription.properties]):
                        if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.imgPath:
                            imgPath = prop[pgKnowledgeGraph.NodePropertyDescription.value]
                            del entry[pgKnowledgeGraph.NodeDescription.properties][propIdx]
                        elif prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.acquisitionCosts:
                            del entry[pgKnowledgeGraph.NodeDescription.properties][propIdx] # info that the user doesn't need to know
                        elif prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.printingSpeed:
                            del entry[pgKnowledgeGraph.NodeDescription.properties][propIdx]
                        else:
                            # translate properties
                            entry[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,entry[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.key]])

                    # fetch colors of that material
                    colorsOfMaterial = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(entry[pgKnowledgeGraph.NodeDescription.nodeID], NodeTypesAM.color)
                    # maybe parse the content of the colorNodeArray
                    # sort out all inactive nodes
                    colors = []
                    for color in colorsOfMaterial:
                        if color[pgKnowledgeGraph.NodeDescription.active] is True:
                            for propIdx, prop in enumerate(color[pgKnowledgeGraph.NodeDescription.properties]):
                                color[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,color[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.key]])
                            colors.append(color)

                    output["materials"].append({"id": entry[pgKnowledgeGraph.NodeDescription.nodeID], "title": entry[pgKnowledgeGraph.NodeDescription.nodeName], "propList": entry[pgKnowledgeGraph.NodeDescription.properties], "imgPath": imgPath, "medianPrice": materialPrices[entry[pgKnowledgeGraph.NodeDescription.uniqueID]] if entry[pgKnowledgeGraph.NodeDescription.uniqueID] in materialPrices else 0., "colors": colors})
                    # TODO use translation here for nodeName
        # sort by price
        output["materials"] = sorted(output["materials"], key=lambda x: x["medianPrice"])

        # mockup here:
        #mock = copy.deepcopy(mocks.materialMock)
        #mock["materials"].extend(resultsOfQueries["materials"])
        #output.update(mock)
        return (output, 200)
    except Exception as e:
        return (e, 500)

##################################################
def logicForSetMaterial(request, validatedInput, functionName) -> tuple[dict|Exception, int]:
    """
    Set a material

    :param request: The request
    :type request: Request
    :return: The material or Exception and status code
    :rtype: dict|Exception, int
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface()
        if interface is None:
            return (Exception(f"Rights not sufficient in {functionName}"), 401)

        projectID = validatedInput[ProjectDescription.projectID]
        processID = validatedInput[ProcessDescription.processID]
        groupID = validatedInput["groupID"]
        material = validatedInput["material"]
        color = validatedInput["color"] if "color" in validatedInput else None

        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupID] = {ServiceDetails.material: material}
        if color is not None:
            updateArray[groupID][ServiceDetails.color] = color
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