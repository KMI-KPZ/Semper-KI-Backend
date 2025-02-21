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
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks
from code_SemperKI.utilities.locales import manageTranslations

from ..definitions import SERVICE_NAME, NodeTypesAM, NodePropertiesAMMaterial, FilterCategories, ServiceDetails, MaterialDetails

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################
def appendHelper(materialEntry:dict, locale:str, materialPrices:dict, output:list):
    """
    Helper function to determine if an entry should be appended to the output list

    :return: True if the entry should be appended, False otherwise
    :rtype: bool
    """
    # prepare properties
    imgPath = mocks.testPicture
    for propIdx, prop in enumerate(materialEntry[pgKnowledgeGraph.NodeDescription.properties]):
        if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.imgPath:
            imgPath = prop[pgKnowledgeGraph.NodePropertyDescription.value]
            del materialEntry[pgKnowledgeGraph.NodeDescription.properties][propIdx]
        elif prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.acquisitionCosts:
            del materialEntry[pgKnowledgeGraph.NodeDescription.properties][propIdx] # info that the user doesn't need to know
        elif prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.printingSpeed:
            del materialEntry[pgKnowledgeGraph.NodeDescription.properties][propIdx]
        else:
            # translate properties
            materialEntry[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,materialEntry[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.key]])

    # fetch colors of that material
    colorsOfMaterial = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(materialEntry[pgKnowledgeGraph.NodeDescription.nodeID], NodeTypesAM.color)
    # maybe parse the content of the colorNodeArray
    # sort out all inactive nodes
    colors = []
    for color in colorsOfMaterial:
        if color[pgKnowledgeGraph.NodeDescription.active] is True:
            for propIdx, prop in enumerate(color[pgKnowledgeGraph.NodeDescription.properties]):
                if prop[pgKnowledgeGraph.NodePropertyDescription.key] == NodePropertiesAMMaterial.imgPath:
                    del color[pgKnowledgeGraph.NodeDescription.properties][propIdx]
                else:
                    color[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,color[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.key]])
            colors.append(color)

    output["materials"].append({MaterialDetails.id: materialEntry[pgKnowledgeGraph.NodeDescription.nodeID], MaterialDetails.title: materialEntry[pgKnowledgeGraph.NodeDescription.nodeName], MaterialDetails.propList: materialEntry[pgKnowledgeGraph.NodeDescription.properties], MaterialDetails.imgPath: imgPath, MaterialDetails.medianPrice: materialPrices[materialEntry[pgKnowledgeGraph.NodeDescription.uniqueID]] if materialEntry[pgKnowledgeGraph.NodeDescription.uniqueID] in materialPrices else 0., MaterialDetails.colors: colors})
    # TODO use translation here for nodeName
    return None
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

        # look for generic filters before filtering the materials for properties
        materialList = []
        typesAreFiltered = -1
        categoriesAreFiltered = -1
        for filterIdx, filterEntry in enumerate(filters["filters"]):
            # see if filter is selected
            if filterEntry["isChecked"] is True:
                # filter for material type
                if filterEntry["question"]["title"] == FilterCategories.materialType.value:
                    if filterEntry["answer"] is not None:
                        typesAreFiltered = filterIdx
                        
                # filter for material category
                if filterEntry["question"]["title"] == FilterCategories.materialCategory.value:
                    if filterEntry["answer"] is not None:
                        categoriesAreFiltered = filterIdx
        
        # apply generic filters
        if typesAreFiltered != -1:
            # materialType is the strictest filter, apply this first
            typeID = filters["filters"][typesAreFiltered]["answer"]["value"] # contains the id of the chosen type node
            typesOfEntry = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(typeID, NodeTypesAM.material) # get materials
            if isinstance(typesOfEntry, Exception):
                raise typesOfEntry
            if categoriesAreFiltered != -1:
                # if the category is also filtered, apply this filter as well
                categoryID = filters["filters"][categoriesAreFiltered]["answer"]["value"] # contains the id of the chosen category node
                for materialNode in typesOfEntry:
                    result = pgKnowledgeGraph.Basics.getIfEdgeExists(materialNode[pgKnowledgeGraph.NodeDescription.nodeID], categoryID)
                    if isinstance(result, Exception):
                        raise result
                    if result:
                        materialList.append(materialNode)
            else:
                materialList = typesOfEntry
        elif categoriesAreFiltered != -1:
            # if only the category is filtered, apply this filter
            categoryID = filters["filters"][categoriesAreFiltered]["answer"]["value"]
            materialList = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(categoryID, NodeTypesAM.material)
        else:
            materialList = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
        
        for entry in materialList:
            # use only entries from system
            if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner and entry[pgKnowledgeGraph.NodeDescription.active] is True:
                # sort out those that have no connection to an organization (and are therefore not in use)
                if len(pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(entry[pgKnowledgeGraph.NodeDescription.uniqueID])) == 1:
                    continue
                
                # adhere to the filters:
                append = True
                for filterEntry in filters["filters"]:
                    # see if filter is selected and the value has not been ruled out somewhere
                    if filterEntry["isChecked"] is True and append is True:
                        
                        # filter for material tensile strenght
                        if filterEntry["question"]["title"] == FilterCategories.tensileStrength.value:
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
                        if filterEntry["question"]["title"] == FilterCategories.density.value:
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
                        if filterEntry["question"]["title"] == FilterCategories.elongationAtBreak.value:
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
                        if filterEntry["question"]["title"] == FilterCategories.certificates.value:
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
                    appendHelper(entry, locale, materialPrices, output)
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
        color = validatedInput["color"] if "color" in validatedInput else {}

        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupID] = {ServiceDetails.material: material}
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