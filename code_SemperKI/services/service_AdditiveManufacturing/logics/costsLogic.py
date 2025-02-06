"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Cost calculations for this service
"""
import math, logging, numpy, sys

from django.conf import settings

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists
from Generic_Backend.code_General.utilities.crypto import encryptObjectWithAES

from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import *

from ..definitions import *
from ..connections.postgresql import pgKG
from ..connections.filterViaSparql import Filter


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

# TODO: THIS WHOLE FILE IS A MESS AND NEEDS TO BE REFACTORED

##################################################
PLATFORM_MARGIN = 10. # random value

##################################################
class Costs():
    """
    Calculate all costs associated with the additive manufacturing process for one organization
    
    """

    ##################################################
    def __init__(self, process:ProcessInterface|Process, additionalArguments:dict, filterObject:Filter, apiGivenContent:dict={}) -> None:
        """
        Gather input variables

        """
        self.processObj = process
        self.additionalArguments = additionalArguments
        self.filterObject = filterObject
        self.detailedCalculations = {} # contains all information about every calculation here, will be encrypted and saved in the process

        # From Organization (do only once)
        organization = {}
        if apiGivenContent == {}:
            organization = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=self.additionalArguments["contractor"][0])
        else:
            organization = apiGivenContent["organization"]
        if checkIfNestedKeyExists(organization, OrganizationDescription.details, OrganizationDetails.services, SERVICE_NAME):
            orgaParameters = organization[OrganizationDescription.details][OrganizationDetails.services][SERVICE_NAME]

            for entry in orgaParameters:
                value = entry[ServiceSpecificFields.value]
                match entry[ServiceSpecificFields.key]:
                    case OrganizationDetailsAM.costRatePersonnelEngineering:
                        self.costRatePersonnelEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.costRatePersonnelEngineering.value] = value
                    case OrganizationDetailsAM.costRateEquipmentEngineering:
                        self.costRateEquipmentEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.costRateEquipmentEngineering.value] = value
                    case OrganizationDetailsAM.repairCosts:
                        self.repairCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.repairCosts.value] = value
                    case OrganizationDetailsAM.safetyGasCosts:
                        self.safetyGasPerHour = value
                        self.detailedCalculations[OrganizationDetailsAM.safetyGasCosts.value] = value
                    case OrganizationDetailsAM.roomCosts:
                        self.roomCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.roomCosts.value] = value
                    case OrganizationDetailsAM.powerCosts:
                        self.powerCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.powerCosts.value] = value
                    case OrganizationDetailsAM.additionalFixedCosts:
                        self.additionalFixedCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.additionalFixedCosts.value] = value
                    case OrganizationDetailsAM.fixedCostsEquipmentEngineering:
                        self.fixedCostsEquipmentEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.fixedCostsEquipmentEngineering.value] = value
                    case OrganizationDetailsAM.margin:
                        self.organizationMargin = value
                        self.detailedCalculations[OrganizationDetailsAM.margin.value] = value
                    case OrganizationDetailsAM.personnelCosts:
                        self.personnelCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.personnelCosts.value] = value
        else:
            self.costRatePersonnelEngineering = 35
            self.costRateEquipmentEngineering = 2
            self.repairCosts = 0.025
            self.safetyGasPerHour = 20
            self.roomCosts = 14.5
            self.powerCosts = 0.17
            self.additionalFixedCosts = 0
            self.fixedCostsEquipmentEngineering = 2
            self.organizationMargin = 0
            self.personnelCosts = 0
            self.detailedCalculations[OrganizationDetailsAM.costRatePersonnelEngineering.value] = self.costRatePersonnelEngineering
            self.detailedCalculations[OrganizationDetailsAM.costRateEquipmentEngineering.value] = self.costRateEquipmentEngineering
            self.detailedCalculations[OrganizationDetailsAM.repairCosts.value] = self.repairCosts
            self.detailedCalculations[OrganizationDetailsAM.safetyGasCosts.value] = self.safetyGasPerHour
            self.detailedCalculations[OrganizationDetailsAM.roomCosts.value] = self.roomCosts
            self.detailedCalculations[OrganizationDetailsAM.powerCosts.value] = self.powerCosts
            self.detailedCalculations[OrganizationDetailsAM.additionalFixedCosts.value] = self.additionalFixedCosts
            self.detailedCalculations[OrganizationDetailsAM.fixedCostsEquipmentEngineering.value] = self.fixedCostsEquipmentEngineering
            self.detailedCalculations[OrganizationDetailsAM.margin.value] = self.organizationMargin
            self.detailedCalculations[OrganizationDetailsAM.personnelCosts.value] = self.personnelCosts
        
    ##################################################
    class PrinterValues(StrEnumExactlyAsDefined):
        """
        Values for every printer
        
        """
        
        technology = enum.auto()
        costRatePersonalMachine = enum.auto()
        buildChamberHeight = enum.auto()
        buildChamberLength = enum.auto()
        buildChamberWidth = enum.auto()
        machineMaterialLoss = enum.auto()
        machineBatchDistance = enum.auto()
        layerThickness = enum.auto()
        machineSurfaceArea = enum.auto()
        machineSetUpSimple = enum.auto()
        machineSetUpComplex = enum.auto()
        averagePowerConsumption = enum.auto()
        machineHourlyRate = enum.auto()
        # Powder Bed fusion only:
        coatingTime = enum.auto()
        # FDM only:
        buildRate = enum.auto()
        fillRate = enum.auto()
        nozzleDiameter = enum.auto()
        maxPrintingSpeed = enum.auto()

    ##################################################
    class MaterialValues(StrEnumExactlyAsDefined):
        """
        Values for every material
        
        """
        
        priceOfSpecificMaterial = enum.auto()
        densityOfSpecificMaterial = enum.auto()
        maxPrintingSpeed = enum.auto()

    ##################################################
    class PostProcessingValues(StrEnumExactlyAsDefined):
        """
        Values for every post processing
        
        """
        
        fixedCostsPostProcessing = enum.auto()
        treatmentCostsPostProcessing = enum.auto()

    ##################################################
    def fetchInformation(self, groupID, group, apiGivenContent:dict={}) -> None|Exception:
        """
        Fetch information about everything
        
        """
        try:
            # From Material
            self.listOfValuesForEveryMaterial = []
            self.minimalPrintingSpeed = sys.float_info.max # largest float
            material = group[ServiceDetails.material]
            valuesForThisMaterial = {}
            valuesForThisMaterial[self.MaterialValues.priceOfSpecificMaterial.value] = float(material.get(NodePropertiesAMMaterial.acquisitionCosts, 400))
            valuesForThisMaterial[self.MaterialValues.densityOfSpecificMaterial.value] = float(material.get(NodePropertiesAMMaterial.density, 4.43))
            if NodePropertiesAMMaterial.printingSpeed in material and material[NodePropertiesAMMaterial.printingSpeed] < self.minimalPrintingSpeed:
                self.minimalPrintingSpeed = float(material[NodePropertiesAMMaterial.printingSpeed])
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["materialParameters"] = valuesForThisMaterial
            self.listOfValuesForEveryMaterial.append(valuesForThisMaterial)

            # From Printer
            if apiGivenContent == {}:
                viablePrintersOfTheManufacturer = self.filterObject.getPrintersOfAContractor(self.additionalArguments["contractor"][0], groupID)
            else:
                viablePrintersOfTheManufacturer = apiGivenContent["printers"]
            self.listOfValuesForEveryPrinter = []
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["printerParameters"] = []
            for printer in viablePrintersOfTheManufacturer:
                valuesForThisPrinter = {}
                # get technology
                technology = "Material Extrusion"
                if apiGivenContent == {}:
                    technologies = pgKG.Basics.getSpecificNeighborsByType(printer[pgKG.NodeDescription.nodeID], pgKG.NodeTypesAM.technology)
                    technology = technologies[0][pgKG.NodeDescription.nodeName] if len(technologies) > 0 else "Material Extrusion"
                else:
                    technology = printer["technology"]
                
                valuesForThisPrinter[self.PrinterValues.technology.value] = technology
                propertiesOfPrinter = printer[pgKG.NodeDescription.properties]
                for entry in propertiesOfPrinter:
                    value = entry[pgKG.NodePropertyDescription.value]
                    match entry[pgKG.NodePropertyDescription.key]:
                        case NodePropertiesAMPrinter.costRatePersonalMachine:
                            valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine.value] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildHeight:
                            valuesForThisPrinter[self.PrinterValues.buildChamberHeight.value] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildLength:
                            valuesForThisPrinter[self.PrinterValues.buildChamberLength.value] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildWidth:
                            valuesForThisPrinter[self.PrinterValues.buildChamberWidth.value] = float(value)
                        case NodePropertiesAMPrinter.lossOfMaterial:
                            valuesForThisPrinter[self.PrinterValues.machineMaterialLoss.value] = float(value)
                        case NodePropertiesAMPrinter.machineBatchDistance:
                            valuesForThisPrinter[self.PrinterValues.machineBatchDistance.value] = float(value)
                        case NodePropertiesAMPrinter.possibleLayerHeights:
                            valuesForThisPrinter[self.PrinterValues.layerThickness.value] = [float(x) for x in value.split(",")].sort(reverse=True)
                        case NodePropertiesAMPrinter.machineSurfaceArea:
                            valuesForThisPrinter[self.PrinterValues.machineSurfaceArea.value] = float(value)
                        case NodePropertiesAMPrinter.simpleMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpSimple.value] = float(value)
                        case NodePropertiesAMPrinter.complexMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpComplex.value] = float(value)
                        case NodePropertiesAMPrinter.averagePowerConsumption:
                            valuesForThisPrinter[self.PrinterValues.averagePowerConsumption.value] = float(value)
                        case NodePropertiesAMPrinter.machineHourlyRate:
                            valuesForThisPrinter[self.PrinterValues.machineHourlyRate.value] = float(value)
                        # Powder Bet fusion:
                        case NodePropertiesAMPrinter.coatingTime:
                            valuesForThisPrinter[self.PrinterValues.coatingTime.value] = float(value)
                        # Extrusion only:
                        case NodePropertiesAMPrinter.buildRate:
                            valuesForThisPrinter[self.PrinterValues.buildRate.value] = float(value)
                        case NodePropertiesAMPrinter.fillRate:
                            valuesForThisPrinter[self.PrinterValues.fillRate.value] = float(value) / 100.
                        case NodePropertiesAMPrinter.nozzleDiameter:
                            valuesForThisPrinter[self.PrinterValues.nozzleDiameter.value] = float(value)
                        case NodePropertiesAMPrinter.maxPrintingSpeed:
                            valuesForThisPrinter[self.PrinterValues.maxPrintingSpeed.value] = float(value)
                        

                # default values
                if NodePropertiesAMPrinter.costRatePersonalMachine not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine.value] = 26
                if NodePropertiesAMPrinter.chamberBuildHeight not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberHeight.value] = 500
                if NodePropertiesAMPrinter.chamberBuildLength not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberLength.value] = 500
                if NodePropertiesAMPrinter.chamberBuildWidth not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberWidth.value] = 500
                if NodePropertiesAMPrinter.lossOfMaterial not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineMaterialLoss.value] = 30
                if NodePropertiesAMPrinter.machineBatchDistance not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineBatchDistance.value] = 10
                if NodePropertiesAMPrinter.possibleLayerHeights not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.layerThickness.value] = [75.]
                if NodePropertiesAMPrinter.machineSurfaceArea not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSurfaceArea.value] = 1.8
                if NodePropertiesAMPrinter.simpleMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpSimple.value] = 1
                if NodePropertiesAMPrinter.complexMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpComplex.value] = 2
                if NodePropertiesAMPrinter.averagePowerConsumption not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.averagePowerConsumption.value] = 5
                if NodePropertiesAMPrinter.machineHourlyRate not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineHourlyRate.value] = 51.80
                # Poweder bed fusion only:
                if NodePropertiesAMPrinter.coatingTime not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.coatingTime.value] = 9
                # Extrusion only:
                if NodePropertiesAMPrinter.fillRate not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.fillRate.value] = 1.0
                if NodePropertiesAMPrinter.nozzleDiameter not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.nozzleDiameter.value] = 0.4
                if NodePropertiesAMPrinter.maxPrintingSpeed not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.maxPrintingSpeed.value] = 60
                # build rate will be calculated in the calculateCostsForPrinter function if not set
                self.listOfValuesForEveryPrinter.append(valuesForThisPrinter)
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["printerParameters"].append(valuesForThisPrinter)

            # From PostProcessing
            self.listOfValuesForEveryPostProcessing = []
            if ServiceDetails.postProcessings in group:
                chosenPostProcessings = group[ServiceDetails.postProcessings]
                for postProcessingID in chosenPostProcessings:
                    postProcessing = chosenPostProcessings[postProcessingID]
                    valuesForThisPostProcessing = {}
                    valuesForThisPostProcessing[self.PostProcessingValues.fixedCostsPostProcessing.value] = float(postProcessing.get(NodePropertiesAMAdditionalRequirement.fixedCosts, 0))
                    valuesForThisPostProcessing[self.PostProcessingValues.treatmentCostsPostProcessing.value] = float(postProcessing.get(NodePropertiesAMAdditionalRequirement.treatmentCosts, 0))
                    self.listOfValuesForEveryPostProcessing.append(valuesForThisPostProcessing)
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["postProcessingParameters"] = self.listOfValuesForEveryPostProcessing
        except Exception as e:
            loggerError.error("Error in fetchInformation: " + str(e))
            return e


    ##################################################
    def calculateCostsForBatches(self, groupID, modelID, printerIdx, printer:dict, exposureTime:float, partLength:float, partHeight:float, partWidth:float, partQuantity:int, layerThickness:float) -> tuple:
        """
        Calculate the costs for the batches
        
        """
        try:
            # C09 - Calculation of max. printed parts in z-dimension, batch distance is only between the parts, first layer and last layer of the chamber is fully used
            theoMaxBatchSizeHeight = math.floor((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) // (partHeight + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theoMaxBatchSizeHeight"] = theoMaxBatchSizeHeight

            # C10 - Calculation of max. printed parts in x-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theoMaxBatchSizeLength = math.floor((printer[self.PrinterValues.buildChamberLength] ) // (partLength + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theoMaxBatchSizeLength"] = theoMaxBatchSizeLength

            # C11 - Calculation of max. printed parts in y-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theoMaxBatchSizeWidth = math.floor((printer[self.PrinterValues.buildChamberWidth] ) // (partWidth + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theoMaxBatchSizeWidth"] = theoMaxBatchSizeWidth

            # C12 - Calculation of max. printed parts in xy-plain
            theoMaxBatchSizeXY = theoMaxBatchSizeLength * theoMaxBatchSizeWidth
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theoMaxBatchSizexy"] = theoMaxBatchSizeXY

            # C13 - Calculation of max. printed parts in chamber
            theoMaxPartsPerBatch = theoMaxBatchSizeXY * theoMaxBatchSizeHeight
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theoMaxPartsPerBatch"] = theoMaxPartsPerBatch

            # C18 - Resulting Bounding-Box volume of x,y,z with batch distance in each dimension
            #volume_bounding_box = (self.partHeight + machineBatchDistance) * (partLength + machineBatchDistance) * (partWidth + machineBatchDistance)

            # C22 - How many batches you need at least to print the quanitity
            minBatchQuantity = math.ceil(partQuantity / theoMaxPartsPerBatch)
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["minBatchQuantity"] = minBatchQuantity

            # C23 - Shows how many parts could be printed in the last batch
            allUnusedBatch = minBatchQuantity * theoMaxPartsPerBatch - partQuantity
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["allUnusedBatch"] = allUnusedBatch

            # C24 - Shows how many bounding boxes in z-dimension is unused
            unusedBatchSizeHeight = allUnusedBatch // theoMaxBatchSizeXY
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["unusedBatchSizeHeight"] = unusedBatchSizeHeight

            # C25 - Shows how many bounding boxes in z-dimension is used
            usedBatchSizeHeight = theoMaxBatchSizeHeight - unusedBatchSizeHeight
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["usedBatchSizeHeight"] = usedBatchSizeHeight

            # C27 - Shows how many bounding boxes in the xy-plain is used
            usedBatchSizeXZ = (theoMaxBatchSizeLength * theoMaxBatchSizeWidth) if partQuantity % theoMaxBatchSizeXY == 0 else partQuantity % theoMaxBatchSizeXY
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["usedBatchSizeXZ"] = usedBatchSizeXZ

            # C26 - Shows how many bounding boxes in the xy-plain is unused
            unusedBatchSizeXZ = theoMaxBatchSizeXY - usedBatchSizeXZ
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["unusedBatchSizeXZ"] = unusedBatchSizeXZ

            # C28 - Checks if used bounding boxes are the same as the part quantity
            quantityCheck = partQuantity == minBatchQuantity * theoMaxBatchSizeHeight * theoMaxBatchSizeXY - unusedBatchSizeHeight * theoMaxBatchSizeXY - unusedBatchSizeXZ
            if quantityCheck is False:
                raise ValueError("Quantity check failed")

            # C30 - Calculates the summ of all unused heigth of the chamber in mm for all batches excluding batch n
            heightOffsetFirstBatchN1 = ((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * theoMaxBatchSizeHeight) * (minBatchQuantity - 1)
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["heightOffsetFirstBatchN1"] = heightOffsetFirstBatchN1

            # C31 - Calculates unused heigth of the chamber in mm for  batch n
            heightOffsetLastBatchN = (printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * usedBatchSizeHeight
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["heightOffsetLastBatchN"] = heightOffsetLastBatchN

            # C32 - Ratio between used chamber height and unused chamber height over all batches
            #chamberHeightFillgrade = 1 - ( (heightOffsetFirstBatchN1 + heightOffsetLastBatchN) / (minBatchQuantity * printer[self.PrinterValues.buildChamberHeight]))

            # C108 - Belichtungszeit Batch =C107*C13
            exposureTimeBatch = exposureTime * theoMaxPartsPerBatch
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["exposureTimeBatch"] = exposureTimeBatch

            # C105 - Beschichtungszeit Batch ==(AUFRUNDEN(((C2*1000)/C77);0)*C94)/3600
            coatingTimeBatch = (math.ceil((printer[self.PrinterValues.buildChamberHeight] * 1000.) / layerThickness) * printer[self.PrinterValues.coatingTime]) / 3600.
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["coatingTimeBatch"] = coatingTimeBatch

            # C106 - Beschichtungszeit Quantity =((AUFRUNDEN((((((C2-C30)*(C22-1))+(C2-C31))*1000)/C77);0)*C94)/3600)
            coatingTimeQuantity = ((math.ceil((((((
                                        printer[self.PrinterValues.buildChamberHeight] - heightOffsetFirstBatchN1) * (
                                        minBatchQuantity - 1)) + (
                                        printer[self.PrinterValues.buildChamberHeight] - heightOffsetLastBatchN)) * 1000.) / layerThickness)) * printer[self.PrinterValues.coatingTime]) / 3600.)
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["coatingTimeQuantity"] = coatingTimeQuantity

            # C79 - Druckdauer Batch =C105+C108
            printDurationBatch = coatingTimeBatch + exposureTimeBatch
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printDurationBatch"] = printDurationBatch

            # C103 - Anzahl an Batches C22
            #anzahlAnBatches = minBatchQuantity

            return printDurationBatch, coatingTimeQuantity, minBatchQuantity, theoMaxPartsPerBatch
        except Exception as e:
            loggerError.error("Error in calculateCostsForBatches: " + str(e))
            return e, e, e, e

    ##################################################
    def calculateCostsForMaterial(self, groupID, modelID, printerIdx, printer:dict, theoMaxPartsPerBatch:int, partVolume:float, partQuantity:int, productComplexity) -> list:
        """
        Calculate the costs for every material

        """
        try:
            totalCostsForEveryMaterial = []
            for material in self.listOfValuesForEveryMaterial: # this assumes that all selected materials are available for the printer, array is only one element long currently
                
                amountOfMaterial = ( (partVolume * printer[self.PrinterValues.fillRate] * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000.)
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["amountOfMaterial"] = amountOfMaterial

                # C41 - material printing cost for the part
                materialCostPrintingPart = amountOfMaterial * material[self.MaterialValues.priceOfSpecificMaterial]
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["materialCostPrintingPart"] = materialCostPrintingPart

                # C43 - material printing cost for the quantity
                materialCostPrintingQuantity = materialCostPrintingPart * partQuantity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["materialCostPrintingQuantity"] = materialCostPrintingQuantity

                # C44 - machine material loss for the part
                costMachineMaterialLossPart = materialCostPrintingPart * (printer[self.PrinterValues.machineMaterialLoss] / 100)
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costMachineMaterialLossPart"] = costMachineMaterialLossPart

                # C46 - cost for material loss per quantity
                costMachineMaterialLossQuantity = costMachineMaterialLossPart * partQuantity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costMachineMaterialLossQuantity"] = costMachineMaterialLossQuantity

                # C59 - support structures part rate
                supportStructuresPartRate = productComplexity*10.

                # C48 - depending on complexity 0 = 0 ; 1 = 10; 2 = 20; 3 = 30
                costSupportStructuresPart = materialCostPrintingPart * supportStructuresPartRate/100.
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costSupportStructuresPart"] = costSupportStructuresPart

                # C50 - cost for support structures per quantity
                costSupportStructuresQuantity = costSupportStructuresPart * partQuantity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costSupportStructuresQuantity"] = costSupportStructuresQuantity

                # C49 - cost for support structures per batch
                costSupportStructuresBatch = costSupportStructuresPart * theoMaxPartsPerBatch
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costSupportStructuresBatch"] = costSupportStructuresBatch

                # C42 - material printing cost for one batch
                materialCostPrintingBatch = materialCostPrintingPart * theoMaxPartsPerBatch
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["materialCostPrintingBatch"] = materialCostPrintingBatch

                # C45 - cost for material loss per batch
                costMachineMaterialLossBatch = costMachineMaterialLossPart * theoMaxPartsPerBatch
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costMachineMaterialLossBatch"] = costMachineMaterialLossBatch

                # C53 - total material cost for the batch
                totalMaterialCostBatch = materialCostPrintingBatch + costMachineMaterialLossBatch + costSupportStructuresBatch
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["totalMaterialCostBatch"] = totalMaterialCostBatch

                # C52 - total material cost for the part
                totalMaterialCostPart = materialCostPrintingPart + costMachineMaterialLossPart + costSupportStructuresPart
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["totalMaterialCostPart"] = totalMaterialCostPart

                totalMaterialCostQuantity = materialCostPrintingQuantity + costMachineMaterialLossQuantity + costSupportStructuresQuantity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["totalMaterialCostQuantity"] = totalMaterialCostQuantity

                totalCostsForEveryMaterial.append( (totalMaterialCostPart, totalMaterialCostQuantity, totalMaterialCostBatch) )
            
            return totalCostsForEveryMaterial
        except Exception as e:
            loggerError.error("Error in calculateCostsForMaterial: " + str(e))
            return e

    ##################################################
    def calculateCostsForPrinter(self, groupID, group) -> dict[list[tuple]]:
        """
        Calculate the costs for every printer

        """
        try:
            printerCostsPerModel = {}
            # for all models
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"] = {}
            for modelID, model in group[ServiceDetails.models].items():
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID] = {}
                levelOfDetail = model.get(FileObjectContent.levelOfDetail, 1)
                if FileObjectContent.isFile in model and model[FileObjectContent.isFile] is False:
                    partQuantity = model[FileObjectContent.quantity] if model[FileObjectContent.quantity] >= 1 else 1
                    productComplexity = model[FileContentsAM.complexity] if model[FileContentsAM.complexity] >= 0 else 0
                    partHeight = model[FileContentsAM.height] if model[FileContentsAM.height] >= 0 else 0
                    partLength = model[FileContentsAM.length] if model[FileContentsAM.length] >= 0 else 0
                    partWidth = model[FileContentsAM.width] if model[FileContentsAM.width] >= 0 else 0
                    if FileContentsAM.volume not in model or model[FileContentsAM.volume] == 0:
                        partVolume = partHeight * partLength * partWidth / 1000. # to cm³
                    else:
                        partVolume = model[FileContentsAM.volume] / 1000. # to cm³
                else:
                    modelID = model[FileObjectContent.id]
                    partQuantity = model.get(FileObjectContent.quantity, 1)
                    partVolume = 0.
                    productComplexity = 1
                    if ServiceDetails.calculations in group:
                        partHeight = group[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._3]
                        partLength = group[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._2]
                        partWidth = group[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._1]
                        volumeOfModel = group[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.volume]
                        boundingBoxVolume = group[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbVolume]
                        machineEpsilon = 7./3 - 4./3 - 1 # Nevermind that, it just calculates the machine epsion to avoid division by zero
                        productComplexity = round( (1. - volumeOfModel / (boundingBoxVolume + machineEpsilon)) * 4.) # scale to [0,4], then assign nearest integer
                        partVolume = volumeOfModel / 1000. # to cm³
                    else:
                        loggerError.error("No calculations available for model")
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["levelOfDetail"] = levelOfDetail
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["partVolume"] = partVolume
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["partQuantity"] = partQuantity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["productComplexity"] = productComplexity
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["partHeight"] = partHeight
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["partLength"] = partLength
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["partWidth"] = partWidth

                # calculate costs for organization

                # C60 - depends on complexity 0 = 0; 1 = 1; 2 = 2; 3 = 4
                personalEngineeringHours = productComplexity if productComplexity < 3 else 4
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["personalEngineeringHours"] = personalEngineeringHours

                # C62 - cost for personal engineering
                costPersonalEngineering = personalEngineeringHours * self.costRatePersonnelEngineering
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costPersonalEngineering"] = costPersonalEngineering

                # C64 - cost for equipment engineering
                costEquipmentEngineering = self.costRateEquipmentEngineering * personalEngineeringHours + self.fixedCostsEquipmentEngineering
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costEquipmentEngineering"] = costEquipmentEngineering

                # C71 - cost equipment
                costEquipment = costEquipmentEngineering # TODO why should that be?! C71 = C64 in Excel sheet
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costEquipment"] = costEquipment

                totalCostsForEveryPrinter = []
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"] = [{} for _ in range(len(self.listOfValuesForEveryPrinter))]
                for printerIdx, printer in enumerate(self.listOfValuesForEveryPrinter):
                    
                    # calculate layer thickness corresponding to the levelOfDetail
                    layerThicknessArrayLength = len(printer[self.PrinterValues.layerThickness])
                    layerThickness = 75. # default value
                    match levelOfDetail:
                        case 0:
                            layerThickness = printer[self.PrinterValues.layerThickness][0]
                        case 1:
                            layerThickness = printer[self.PrinterValues.layerThickness][int(math.ceil(layerThicknessArrayLength / 2)) - 1]
                        case 2:
                            layerThickness = printer[self.PrinterValues.layerThickness][layerThicknessArrayLength - 1]
                            
                    
                        

                    printingSpeedForMaterialAndPrinter = self.minimalPrintingSpeed
                    # if extrusion printer and build rate is not set, calculate it
                    if printingSpeedForMaterialAndPrinter > printer[self.PrinterValues.maxPrintingSpeed]:
                        printingSpeedForMaterialAndPrinter = printer[self.PrinterValues.maxPrintingSpeed]
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printingSpeedForMaterialAndPrinter"] = printingSpeedForMaterialAndPrinter

                    buildRateForThisPrinter = 0
                    if printer[self.PrinterValues.technology] == "Material Extrusion":
                        if self.PrinterValues.buildRate not in printer:
                            buildRateForThisPrinter = (printer[self.PrinterValues.nozzleDiameter] / 10. )* (layerThickness / 10000.) * printingSpeedForMaterialAndPrinter # converted values to cm so that unit is cm^3/h
                        else:
                            buildRateForThisPrinter = printer[self.PrinterValues.buildRate]
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["buildRateForThisPrinter"] = buildRateForThisPrinter

                    # C81 - schichten_part =AUFRUNDEN((C15*1000)/C77;0)
                    layersPart =  math.ceil((partHeight * 1000) / layerThickness)
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["layersPart"] = layersPart

                    # C89 - Flächennutzung der Maschine =AUFRUNDEN(C88*1,25;0) - Flächenfaktormethode nach Rockstroh ca. +25%
                    machineAreaUsage = math.ceil(printer[self.PrinterValues.machineSurfaceArea] * 1.25)
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machineAreaUsage"] = machineAreaUsage

                    # C91 - Flächennutzungskosten =C89*C90
                    areaUsageCosts = machineAreaUsage * self.roomCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["areaUsageCosts"] = areaUsageCosts

                    # 92 - Stundensatz für Flächennutzung - Berechnung des Stundensatzes für die Fläche =(C91/30)/24 #TODO (wieso /30 nicht 60)??
                    hourlyRateForAreaUsage = (areaUsageCosts / 30.) / 24.
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["hourlyRateForAreaUsage"] = hourlyRateForAreaUsage

                    # C96 - Kosten Strom pro Stunde =C83*C82
                    electricityCostPerHour = printer[self.PrinterValues.averagePowerConsumption] * self.powerCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["electricityCostPerHour"] = electricityCostPerHour

                    # C68 - cost for personal machine
                    costPersonalMachine = printer[self.PrinterValues.costRatePersonalMachine] * (printer[self.PrinterValues.machineSetUpSimple] + printer[self.PrinterValues.machineSetUpComplex])
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costPersonalMachine"] = costPersonalMachine

                    # C70 - cost personal pre process
                    costPersonalPreProcess = costPersonalEngineering + costPersonalMachine
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costPersonalPreProcess"] = costPersonalPreProcess

                    # C72 - cost pre process
                    costPreProcessTotal = costPersonalPreProcess + costEquipment
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costPreProcessTotal"] = costPreProcessTotal

                    # C97 - Allgemeiner Abschreibungssatz =C76
                    amortizationRate = printer[self.PrinterValues.machineHourlyRate]
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["amortizationRate"] = amortizationRate

                    # C98 - Reparatur =C97*C84
                    repair = amortizationRate * self.repairCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["repair"] = repair

                    # C100 - Fläche =C92
                    area = hourlyRateForAreaUsage
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["area"] = area

                    # C104 - Beschichtungszeit Part =(C81*C94)/3600
                    coatingDurationPart = (layersPart * printer[self.PrinterValues.coatingTime]) / 3600.
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["coatingDurationPart"] = coatingDurationPart

                    # C107 - Belichtungszeit ein Teil =((C94*C81)/3600)
                    exposureTimeSinglePart = (printer[self.PrinterValues.coatingTime]  * layersPart) / 3600.
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["exposureTimeSinglePart"] = exposureTimeSinglePart

                    printDurationBatch, coatingTimeQuantity, minBatchQuantity, theoMaxPartsPerBatch = self.calculateCostsForBatches(groupID, modelID, printerIdx, printer, exposureTimeSinglePart, partLength, partHeight, partWidth, partQuantity, layerThickness)

                    listOfCostsForMaterial = self.calculateCostsForMaterial(groupID, modelID, printerIdx, printer, theoMaxPartsPerBatch, partVolume, partQuantity, productComplexity)

                    # C109 - Belichtungszeit Quantity =((C94*C81)/3600)*C21
                    exposureTimeQuantity = ((printer[self.PrinterValues.coatingTime] * layersPart) / 3600.) * partQuantity
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["exposureTimeQuantity"] = exposureTimeQuantity

                    printDurationPart = coatingDurationPart + exposureTimeSinglePart
                    printDurationQuantity = coatingTimeQuantity + exposureTimeQuantity
                    if printer[self.PrinterValues.technology] == "Powder Bed Fusion":
                        # C78 - Druckdauer Part =C104+C107
                        printDurationPart = coatingDurationPart + exposureTimeSinglePart
                        self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printDurationPart"] = printDurationPart

                        # C80 - Druckdauer Quantity =C106+C109
                        printDurationQuantity = coatingTimeQuantity + exposureTimeQuantity
                        self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printDurationQuantity"] = printDurationQuantity
                    if printer[self.PrinterValues.technology] == "Material Extrusion":
                        # C78 - Druckdauer Part =C104+C107
                        printDurationPart = 2.5 * partVolume * printer[self.PrinterValues.fillRate] / buildRateForThisPrinter # the 2.5 is an empirical value
                        self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printDurationPart"] = printDurationPart

                        # C80 - Druckdauer Quantity =C106+C109
                        printDurationQuantity = printDurationPart * partQuantity
                        self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printDurationQuantity"] = printDurationQuantity

                    # C99 - Schutzgas =C87
                    safetyGas = self.safetyGasPerHour
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["safetyGas"] = safetyGas

                    # C102 =SUMME(C96:C100)
                    totalMachineHourlyRate = electricityCostPerHour + amortizationRate + repair + safetyGas + area
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["totalMachineHourlyRate"] = totalMachineHourlyRate

                    # C112 - Maschinenkosten Druckprozess Batch =C79*C102
                    machineCostsPrintProcessBatch = printDurationBatch * totalMachineHourlyRate
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machineCostsPrintProcessBatch"] = machineCostsPrintProcessBatch

                    # C111 - Maschinenkosten Druckprozess Part =C78*C102
                    machineCostsPrintProcessPart = printDurationPart * totalMachineHourlyRate
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machineCostsPrintProcessPart"] = machineCostsPrintProcessPart

                    # C113 - Maschinenkosten Druckprozess Quantity =C80*C102
                    machineCostsPrintProcessQuantity = printDurationQuantity * totalMachineHourlyRate
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machineCostsPrintProcessQuantity"] = machineCostsPrintProcessQuantity

                    # C114 - Personalkosten Druckprozess =(C22-1)*C68
                    personalkostenPrintProcess = (minBatchQuantity - 1) * costPersonalMachine + self.personnelCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["personalkostenPrintProcess"] = personalkostenPrintProcess

                    costsTotalForPrinterPart = machineCostsPrintProcessPart + personalkostenPrintProcess + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterPart"] = costsTotalForPrinterPart
                    costsTotalForPrinterQuantity = machineCostsPrintProcessQuantity + personalkostenPrintProcess + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterQuantity"] = costsTotalForPrinterQuantity
                    costsTotalForPrinterBatch = machineCostsPrintProcessBatch + personalkostenPrintProcess + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterBatch"] = costsTotalForPrinterBatch
                    # TODO save results in a useful datastructure
                    totalCostsForEveryPrinter.append((costsTotalForPrinterPart, costsTotalForPrinterQuantity, costsTotalForPrinterBatch, listOfCostsForMaterial))
                
                printerCostsPerModel[model[FileObjectContent.id]] = totalCostsForEveryPrinter
            return printerCostsPerModel
        except Exception as e:
            loggerError.error("Error in calculateCostsForPrinter: " + str(e))
            return e
    ####################################################################################################

    ##################################################
    def calculateCostsForPostProcessings(self, groupID:int, group:dict) -> list[float]:
        """
        Calculate the costs for the post processings

        """
        try:
            totalCostsForEveryPostProcessing = []
            self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsForEveryPostProcessing"] = [{} for _ in range(len(self.listOfValuesForEveryPostProcessing))]
            for postProcessingIdx, postProcessing in enumerate(self.listOfValuesForEveryPostProcessing):
                # C115 - Total costs for post processing
                totalPostProcessingCosts = postProcessing[self.PostProcessingValues.fixedCostsPostProcessing] + postProcessing[self.PostProcessingValues.treatmentCostsPostProcessing]
                self.detailedCalculations[ServiceDetails.groups.value][groupID]["costsForEveryPostProcessing"][postProcessingIdx]["totalPostProcessingCosts"] = totalPostProcessingCosts

                totalCostsForEveryPostProcessing.append(totalPostProcessingCosts)

            return totalCostsForEveryPostProcessing
        except Exception as e:
            loggerError.error("Error in calculateCostsForPostProcessings: " + str(e))
            return e
    
    ####################################################################################################
    def calculateCosts(self, apiGivenValues:dict={}) -> list[tuple[float,float]]|Exception:
        """
        Calculate all costs
        
        """
        try: 
            costsPerGroup = []
            content = self.processObj.serviceDetails[ServiceDetails.groups.value] if apiGivenValues == {} else apiGivenValues[ServiceDetails.groups.value] 
            self.detailedCalculations[ServiceDetails.groups.value] = [{} for _ in range(len(content))]
            for groupIdx, group in enumerate(content):
                if apiGivenValues == {} and "contractor" in self.additionalArguments and groupIdx not in self.additionalArguments["contractor"][2]:
                    costsPerGroup.append((0., 0.))
                    continue
                retVal = self.fetchInformation(groupIdx, group, apiGivenContent=apiGivenValues)
                if retVal is not None:
                    raise retVal
                printerCostDict = self.calculateCostsForPrinter(groupIdx, group)
                if isinstance(printerCostDict, Exception):
                    raise printerCostDict
                postProcessingCostList = self.calculateCostsForPostProcessings(groupIdx, group)
                if isinstance(postProcessingCostList, Exception):
                    raise postProcessingCostList
                
                postProcessingsCosts = numpy.sum(postProcessingCostList)
                marginOrganization = 1. + self.organizationMargin/100.
                self.detailedCalculations[ServiceDetails.groups.value][groupIdx]["marginOrganization"] = marginOrganization
                
                marginPlattform = 1. + PLATFORM_MARGIN/100.
                self.detailedCalculations[ServiceDetails.groups.value][groupIdx]["marginPlattform"] = marginPlattform

                maximumCosts = [0., 0., 0.] # part, quantity, batch
                minimumCosts = [sys.float_info.max, sys.float_info.max, sys.float_info.max]
                maximumCostsPerFile = {}
                minimumCostsPerFile = {}
                for fileID , printerCostList in printerCostDict.items():
                    maximumCostsThisFile = [0., 0., 0.] # part, quantity, batch
                    minimumCostsThisFile = [sys.float_info.max, sys.float_info.max, sys.float_info.max]
                    for costsTotalForPrinterPart, costsTotalForPrinterQuantity, costsTotalForPrinterBatch, listOfCostsForMaterial in printerCostList:
                        for total_material_cost_part, total_material_cost_quantity, total_material_cost_batch in listOfCostsForMaterial:
                            costsTotal = costsTotalForPrinterPart + total_material_cost_part + postProcessingsCosts
                            if costsTotal > maximumCostsThisFile[0]:
                                maximumCostsThisFile[0] = costsTotal
                            if costsTotal < minimumCostsThisFile[0]:
                                minimumCostsThisFile[0] = costsTotal
                            costsTotal = costsTotalForPrinterQuantity + total_material_cost_quantity + postProcessingsCosts
                            if costsTotal > maximumCostsThisFile[1]:
                                maximumCostsThisFile[1] = costsTotal
                            if costsTotal < minimumCostsThisFile[1]:
                                minimumCostsThisFile[1] = costsTotal
                            costsTotal = costsTotalForPrinterBatch + total_material_cost_batch + postProcessingsCosts
                            if costsTotal > maximumCostsThisFile[2]:
                                maximumCostsThisFile[2] = costsTotal
                            if costsTotal < minimumCostsThisFile[2]:
                                minimumCostsThisFile[2] = costsTotal
                    maximumCostsPerFile[fileID] = maximumCostsThisFile
                    minimumCostsPerFile[fileID] = minimumCostsThisFile

                    for i in range(3):
                        if maximumCostsThisFile[i] > maximumCosts[i]:
                            maximumCosts[i] = maximumCostsThisFile[i]
                        if minimumCostsThisFile[i] < minimumCosts[i]:
                            minimumCosts[i] = minimumCostsThisFile[i]

                    self.detailedCalculations[ServiceDetails.groups.value][groupIdx][fileID] = {}
                    self.detailedCalculations[ServiceDetails.groups.value][groupIdx][fileID]["maximumCostsThisFile"] = maximumCostsThisFile
                    self.detailedCalculations[ServiceDetails.groups.value][groupIdx][fileID]["minimumCostsThisFile"] = minimumCostsThisFile
                    

                totalCosts = [(minimumCosts[0]*marginOrganization*marginPlattform, maximumCosts[0]*marginOrganization*marginPlattform), (minimumCosts[1]*marginOrganization*marginPlattform, maximumCosts[1]*marginOrganization*marginPlattform), (minimumCosts[2]*marginOrganization*marginPlattform, maximumCosts[2]*marginOrganization*marginPlattform)]
                for i in range(len(totalCosts)):
                    left, right = totalCosts[i]
                    if numpy.isnan(left) or not numpy.isfinite(left):
                        left = -1.
                    if numpy.isnan(right) or not numpy.isfinite(right):
                        right = -1.
                    totalCosts[i] = (left, right)
                self.detailedCalculations[ServiceDetails.groups.value][groupIdx]["totalCosts"] = totalCosts
                costsPerGroup.append(totalCosts[1]) # return the costs for quantity
                
            return costsPerGroup
        except Exception as e:
            loggerError.error("Error in calculateCosts: " + str(e))
            return e
        
    ####################################################################################################
    def getEncryptedCostOverview(self) -> str:
        """
        Encrypt the detailed cost overview
        
        :return: encrypted cost overview as str
        :rtype: str
        """
        return encryptObjectWithAES(settings.AES_ENCRYPTION_KEY,self.detailedCalculations)
    

##################################################
def logicForCosts(apiGivenValues:dict={}) -> dict|Exception:
    """
    Logic for the costs

    :param apiGivenValues: the values given by the api
    :type apiGivenValues: dict
    :return: the costs
    :rtype: list[tuple[float,float]]
    """
    try:
        postProcessingObjects = {}
        for postProcessingID, values in apiGivenValues["postProcessings"].items():
            postProcessingObjects[postProcessingID] = {}
            for key, value in values.items():
                postProcessingObjects[postProcessingID][key] = float(value.split(" ")[0])
        
        modelObjects = {}
        for modelID, values in apiGivenValues["models"].items():
            modelObjects[modelID] = {}
            modelObjects[modelID]["isFile"] = False
            for key, value in values.items():
                if key == "id":
                    modelObjects[modelID][key] = value
                else:
                    if isinstance(value, int):
                        modelObjects[modelID][key] = value
                    else:
                        modelObjects[modelID][key] = float(value.split(" ")[0])

        printersArray = []
        for printer in apiGivenValues["printers"]:
            printerObject = {}
            printerObject["technology"] = printer["technology"]
            printerObject["properties"] = []
            for key, value in printer["properties"].items():
                if key == "possibleLayerHeights":
                    printerObject["properties"].append({"name": key, "value": value})
                    continue
                printerObject["properties"].append({"name": key, "value": float(value.split(" ")[0])})
            printersArray.append(printerObject)

        inputDict = {
            "organization": {
                "details":
                {
                    "services": {
                        "ADDITIVE_MANUFACTURING":
                        [
                            {"key":"powerCosts", "value": float(apiGivenValues["organization"]["powerCosts"].split(" ")[0]), "unit": "€/kWh"},
                            {"key":"margin", "value": float(apiGivenValues["organization"]["margin"].split(" ")[0]), "unit": "%"},
                            {"key":"personnelCosts", "value": float(apiGivenValues["organization"]["personnelCosts"].split(" ")[0]), "unit": "€/h"},
                            {"key":"costRatePersonnelEngineering", "value": float(apiGivenValues["organization"]["costRatePersonnelEngineering"].split(" ")[0]), "unit": "€/h" },
                            {"key":"repairCosts", "value": float(apiGivenValues["organization"]["repairCosts"].split(" ")[0]), "unit": "%" },
                            {"key":"additionalFixedCosts", "value": float(apiGivenValues["organization"]["additionalFixedCosts"].split(" ")[0]), "unit": "€" },
                            {"key":"costRateEquipmentEngineering", "value": float(apiGivenValues["organization"]["costRateEquipmentEngineering"].split(" ")[0]), "unit": "€/h" },
                            {"key":"fixedCostsEquipmentEngineering", "value": float(apiGivenValues["organization"]["fixedCostsEquipmentEngineering"].split(" ")[0]), "unit": "€/kWh" },
                            {"key":"safetyGasCosts", "value": float(apiGivenValues["organization"]["safetyGasCosts"].split(" ")[0]), "unit": "€/h" },
                            {"key":"roomCosts", "value": float(apiGivenValues["organization"]["roomCosts"].split(" ")[0]), "unit": "€/m²" }
                        ]
                    }
                }
            },
            "groups": [
                {
                    "material": {
                        "density": float(apiGivenValues["material"]["density"].split(" ")[0]),
                        "printingSpeed": float(apiGivenValues["material"]["printingSpeed"].split(" ")[0]),
                        "acquisitionCosts": float(apiGivenValues["material"]["acquisitionCosts"].split(" ")[0])
                    },
                    "postProcessings": postProcessingObjects,
                    "models": modelObjects
                }
            ],
            "printers": printersArray
        }

        costsObj = Costs({}, {}, {}, inputDict)
        costs = costsObj.calculateCosts(inputDict)
        if isinstance(costs, Exception):
            raise costs
        detailedCalculations = costsObj.detailedCalculations
        outDict = {"costs": costs, "detailedCalculations": detailedCalculations}
        return outDict, 200
    except Exception as e:
        loggerError.error("Error in logicForCosts: " + str(e))
        return e, 500