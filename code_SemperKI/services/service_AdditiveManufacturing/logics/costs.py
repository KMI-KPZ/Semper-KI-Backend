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
    def __init__(self, process:ProcessInterface|Process, additionalArguments:dict, filterObject:Filter) -> None:
        """
        Gather input variables

        """
        self.processObj = process
        self.additionalArguments = additionalArguments
        self.filterObject = filterObject
        self.detailedCalculations = {} # contains all information about every calculation here, will be encrypted and saved in the process

        # From Organization (do only once)
        organization = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=self.additionalArguments["orgaID"])
        if checkIfNestedKeyExists(organization, OrganizationDescription.details, OrganizationDetails.services, SERVICE_NAME) == True:
            orgaParameters = organization[OrganizationDescription.details][OrganizationDetails.services][SERVICE_NAME]

            for entry in orgaParameters:
                value = entry[ServiceSpecificFields.value]
                match entry[ServiceSpecificFields.key]:
                    case OrganizationDetailsAM.costRatePersonnelEngineering:
                        self.costRatePersonnelEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.costRatePersonnelEngineering] = value
                    case OrganizationDetailsAM.costRateEquipmentEngineering:
                        self.costRateEquipmentEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.costRateEquipmentEngineering] = value
                    case OrganizationDetailsAM.repairCosts:
                        self.repairCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.repairCosts] = value
                    case OrganizationDetailsAM.safetyGasCosts:
                        self.safetyGasPerHour = value
                        self.detailedCalculations[OrganizationDetailsAM.safetyGasCosts] = value
                    case OrganizationDetailsAM.roomCosts:
                        self.roomCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.roomCosts] = value
                    case OrganizationDetailsAM.powerCosts:
                        self.powerCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.powerCosts] = value
                    case OrganizationDetailsAM.additionalFixedCosts:
                        self.additionalFixedCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.additionalFixedCosts] = value
                    case OrganizationDetailsAM.fixedCostsEquipmentEngineering:
                        self.fixedCostsEquipmentEngineering = value
                        self.detailedCalculations[OrganizationDetailsAM.fixedCostsEquipmentEngineering] = value
                    case OrganizationDetailsAM.margin:
                        self.organizationMargin = value
                        self.detailedCalculations[OrganizationDetailsAM.margin] = value
                    case OrganizationDetailsAM.personnelCosts:
                        self.personnelCosts = value
                        self.detailedCalculations[OrganizationDetailsAM.personnelCosts] = value
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
            self.detailedCalculations[OrganizationDetailsAM.costRatePersonnelEngineering] = self.costRatePersonnelEngineering
            self.detailedCalculations[OrganizationDetailsAM.costRateEquipmentEngineering] = self.costRateEquipmentEngineering
            self.detailedCalculations[OrganizationDetailsAM.repairCosts] = self.repairCosts
            self.detailedCalculations[OrganizationDetailsAM.safetyGasCosts] = self.safetyGasPerHour
            self.detailedCalculations[OrganizationDetailsAM.roomCosts] = self.roomCosts
            self.detailedCalculations[OrganizationDetailsAM.powerCosts] = self.powerCosts
            self.detailedCalculations[OrganizationDetailsAM.additionalFixedCosts] = self.additionalFixedCosts
            self.detailedCalculations[OrganizationDetailsAM.fixedCostsEquipmentEngineering] = self.fixedCostsEquipmentEngineering
            self.detailedCalculations[OrganizationDetailsAM.margin] = self.organizationMargin
            self.detailedCalculations[OrganizationDetailsAM.personnelCosts] = self.personnelCosts
        
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
    def fetchInformation(self, groupID, group) -> None|Exception:
        """
        Fetch information about everything
        
        """
        try:
            # From Material
            self.listOfValuesForEveryMaterial = []
            self.minimalPrintingSpeed = sys.float_info.max # largest float
            material = group[ServiceDetails.material]
            valuesForThisMaterial = {}
            valuesForThisMaterial[self.MaterialValues.priceOfSpecificMaterial] = float(material.get(NodePropertiesAMMaterial.acquisitionCosts, 400))
            valuesForThisMaterial[self.MaterialValues.densityOfSpecificMaterial] = float(material.get(NodePropertiesAMMaterial.density, 4.43))
            if NodePropertiesAMMaterial.printingSpeed in material and material[NodePropertiesAMMaterial.printingSpeed] < self.minimalPrintingSpeed:
                self.minimalPrintingSpeed = float(material[NodePropertiesAMMaterial.printingSpeed])
            self.detailedCalculations[ServiceDetails.groups][groupID]["materialParameters"] = valuesForThisMaterial
            self.listOfValuesForEveryMaterial.append(valuesForThisMaterial)

            # From Printer
            viablePrintersOfTheManufacturer = self.filterObject.getPrintersOfAContractor(self.additionalArguments["orgaID"], groupID)
            self.listOfValuesForEveryPrinter = []
            self.detailedCalculations[ServiceDetails.groups][groupID]["printerParameters"] = []
            for printer in viablePrintersOfTheManufacturer:
                valuesForThisPrinter = {}
                # get technology
                technologies = pgKG.Basics.getSpecificNeighborsByType(printer[pgKG.NodeDescription.nodeID], pgKG.NodeTypesAM.technology)
                technology = technologies[0][pgKG.NodeDescription.nodeName] if len(technologies) > 0 else "Material Extrusion"
                valuesForThisPrinter[self.PrinterValues.technology] = technology
                propertiesOfPrinter = printer[pgKG.NodeDescription.properties]
                for entry in propertiesOfPrinter:
                    value = entry[pgKG.NodePropertyDescription.value]
                    match entry[pgKG.NodePropertyDescription.name]:
                        case NodePropertiesAMPrinter.costRatePersonalMachine:
                            valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildHeight:
                            valuesForThisPrinter[self.PrinterValues.buildChamberHeight] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildLength:
                            valuesForThisPrinter[self.PrinterValues.buildChamberLength] = float(value)
                        case NodePropertiesAMPrinter.chamberBuildWidth:
                            valuesForThisPrinter[self.PrinterValues.buildChamberWidth] = float(value)
                        case NodePropertiesAMPrinter.lossOfMaterial:
                            valuesForThisPrinter[self.PrinterValues.machineMaterialLoss] = float(value)
                        case NodePropertiesAMPrinter.machineBatchDistance:
                            valuesForThisPrinter[self.PrinterValues.machineBatchDistance] = float(value)
                        case NodePropertiesAMPrinter.possibleLayerHeights:
                            valuesForThisPrinter[self.PrinterValues.layerThickness] = float(value.split(",")[0])
                        case NodePropertiesAMPrinter.machineSurfaceArea:
                            valuesForThisPrinter[self.PrinterValues.machineSurfaceArea] = float(value)
                        case NodePropertiesAMPrinter.simpleMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpSimple] = float(value)
                        case NodePropertiesAMPrinter.complexMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpComplex] = float(value)
                        case NodePropertiesAMPrinter.averagePowerConsumption:
                            valuesForThisPrinter[self.PrinterValues.averagePowerConsumption] = float(value)
                        case NodePropertiesAMPrinter.machineHourlyRate:
                            valuesForThisPrinter[self.PrinterValues.machineHourlyRate] = float(value)
                        # Powder Bet fusion:
                        case NodePropertiesAMPrinter.coatingTime:
                            valuesForThisPrinter[self.PrinterValues.coatingTime] = float(value)
                        # Extrusion only:
                        case NodePropertiesAMPrinter.buildRate:
                            valuesForThisPrinter[self.PrinterValues.buildRate] = float(value)
                        case NodePropertiesAMPrinter.fillRate:
                            valuesForThisPrinter[self.PrinterValues.fillRate] = float(value) / 100.
                        case NodePropertiesAMPrinter.nozzleDiameter:
                            valuesForThisPrinter[self.PrinterValues.nozzleDiameter] = float(value)
                        case NodePropertiesAMPrinter.maxPrintingSpeed:
                            valuesForThisPrinter[self.PrinterValues.maxPrintingSpeed] = float(value)
                        

                # default values
                if NodePropertiesAMPrinter.costRatePersonalMachine not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine] = 26
                if NodePropertiesAMPrinter.chamberBuildHeight not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberHeight] = 500
                if NodePropertiesAMPrinter.chamberBuildLength not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberLength] = 500
                if NodePropertiesAMPrinter.chamberBuildWidth not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.buildChamberWidth] = 500
                if NodePropertiesAMPrinter.lossOfMaterial not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineMaterialLoss] = 30
                if NodePropertiesAMPrinter.machineBatchDistance not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineBatchDistance] = 10
                if NodePropertiesAMPrinter.possibleLayerHeights not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.layerThickness] = 75
                if NodePropertiesAMPrinter.machineSurfaceArea not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSurfaceArea] = 1.8
                if NodePropertiesAMPrinter.simpleMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpSimple] = 1
                if NodePropertiesAMPrinter.complexMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpComplex] = 2
                if NodePropertiesAMPrinter.averagePowerConsumption not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.averagePowerConsumption] = 5
                if NodePropertiesAMPrinter.machineHourlyRate not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineHourlyRate] = 51.80
                # Poweder bed fusion only:
                if NodePropertiesAMPrinter.coatingTime not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.coatingTime] = 9
                # Extrusion only:
                if NodePropertiesAMPrinter.fillRate not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.fillRate] = 1.0
                if NodePropertiesAMPrinter.nozzleDiameter not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.nozzleDiameter] = 0.4
                if NodePropertiesAMPrinter.maxPrintingSpeed not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.maxPrintingSpeed] = 60
                # build rate will be calculated in the calculateCostsForPrinter function if not set
                self.listOfValuesForEveryPrinter.append(valuesForThisPrinter)
                self.detailedCalculations[ServiceDetails.groups][groupID]["printerParameters"].append(valuesForThisPrinter)

            # From PostProcessing
            self.listOfValuesForEveryPostProcessing = []
            if ServiceDetails.postProcessings in group:
                chosenPostProcessings = group[ServiceDetails.postProcessings]
                for postProcessingID in chosenPostProcessings:
                    postProcessing = chosenPostProcessings[postProcessingID]
                    valuesForThisPostProcessing = {}
                    valuesForThisPostProcessing[self.PostProcessingValues.fixedCostsPostProcessing] = float(postProcessing.get(NodePropertiesAMAdditionalRequirement.fixedCosts, 0))
                    valuesForThisPostProcessing[self.PostProcessingValues.treatmentCostsPostProcessing] = float(postProcessing.get(NodePropertiesAMAdditionalRequirement.treatmentCosts, 0))
                    self.listOfValuesForEveryPostProcessing.append(valuesForThisPostProcessing)
                self.detailedCalculations[ServiceDetails.groups][groupID]["postProcessingParameters"] = self.listOfValuesForEveryPostProcessing
        except Exception as e:
            loggerError.error("Error in fetchInformation: " + str(e))
            return e


    ##################################################
    def calculateCostsForBatches(self, groupID, modelID, printerIdx, printer:dict, exposureTime:float, partLength:float, partHeight:float, partWidth:float, partQuantity:int) -> tuple:
        """
        Calculate the costs for the batches
        
        """
        try:
            # C09 - Calculation of max. printed parts in z-dimension, batch distance is only between the parts, first layer and last layer of the chamber is fully used
            theo_max_Batch_size_height = math.floor((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) // (partHeight + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theo_max_Batch_size_height"] = theo_max_Batch_size_height

            # C10 - Calculation of max. printed parts in x-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theo_max_Batch_size_length = math.floor((printer[self.PrinterValues.buildChamberLength] ) // (partLength + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theo_max_Batch_size_length"] = theo_max_Batch_size_length

            # C11 - Calculation of max. printed parts in y-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theo_max_Batch_size_width = math.floor((printer[self.PrinterValues.buildChamberWidth] ) // (partWidth + printer[self.PrinterValues.machineBatchDistance]))
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theo_max_Batch_size_width"] = theo_max_Batch_size_width

            # C12 - Calculation of max. printed parts in xy-plain
            theo_max_batch_size_xy = theo_max_Batch_size_length * theo_max_Batch_size_width
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theo_max_batch_size_xy"] = theo_max_batch_size_xy

            # C13 - Calculation of max. printed parts in chamber
            theo_max_parts_per_batch = theo_max_batch_size_xy * theo_max_Batch_size_height
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["theo_max_parts_per_batch"] = theo_max_parts_per_batch

            # C18 - Resulting Bounding-Box volume of x,y,z with batch distance in each dimension
            #volume_bounding_box = (self.partHeight + machineBatchDistance) * (partLength + machineBatchDistance) * (partWidth + machineBatchDistance)

            # C22 - How many batches you need at least to print the quanitity
            min_batch_quantity = math.ceil(partQuantity / theo_max_parts_per_batch)
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["min_batch_quantity"] = min_batch_quantity

            # C23 - Shows how many parts could be printed in the last batch
            all_unused_batch = min_batch_quantity * theo_max_parts_per_batch - partQuantity
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["all_unused_batch"] = all_unused_batch

            # C24 - Shows how many bounding boxes in z-dimension is unused
            unused_batch_size_height = all_unused_batch // theo_max_batch_size_xy
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["unused_batch_size_height"] = unused_batch_size_height

            # C25 - Shows how many bounding boxes in z-dimension is used
            used_batch_size_height = theo_max_Batch_size_height - unused_batch_size_height
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["used_batch_size_height"] = used_batch_size_height

            # C27 - Shows how many bounding boxes in the xy-plain is used
            used_batch_size_xz = (theo_max_Batch_size_length * theo_max_Batch_size_width) if partQuantity % theo_max_batch_size_xy == 0 else partQuantity % theo_max_batch_size_xy
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["used_batch_size_xz"] = used_batch_size_xz

            # C26 - Shows how many bounding boxes in the xy-plain is unused
            unused_batch_size_xz = theo_max_batch_size_xy - used_batch_size_xz
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["unused_batch_size_xz"] = unused_batch_size_xz

            # C28 - Checks if used bounding boxes are the same as the part quantity
            quantity_check = partQuantity == min_batch_quantity * theo_max_Batch_size_height * theo_max_batch_size_xy - unused_batch_size_height * theo_max_batch_size_xy - unused_batch_size_xz
            if quantity_check == False:
                raise ValueError("Quantity check failed")

            # C30 - Calculates the summ of all unused heigth of the chamber in mm for all batches excluding batch n
            height_offset_first_batch_n_1 = ((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * theo_max_Batch_size_height) * (min_batch_quantity - 1)
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["height_offset_first_batch_n_1"] = height_offset_first_batch_n_1

            # C31 - Calculates unused heigth of the chamber in mm for  batch n
            height_offset_last_batch_n = (printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * used_batch_size_height
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["height_offset_last_batch_n"] = height_offset_last_batch_n

            # C32 - Ratio between used chamber height and unused chamber height over all batches
            #chamber_height_fillgrade = 1 - ( (height_offset_first_batch_n_1 + height_offset_last_batch_n) / (min_batch_quantity * printer[self.PrinterValues.buildChamberHeight]))

            # C108 - Belichtungszeit Batch =C107*C13
            belichtungszeit_batch = exposureTime * theo_max_parts_per_batch
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["belichtungszeit_batch"] = belichtungszeit_batch

            # C105 - Beschichtungszeit Batch ==(AUFRUNDEN(((C2*1000)/C77);0)*C94)/3600
            beschichtungszeit_batch = (math.ceil((printer[self.PrinterValues.buildChamberHeight] * 1000.) / printer[self.PrinterValues.layerThickness]) * printer[self.PrinterValues.coatingTime]) / 3600.
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["beschichtungszeit_batch"] = beschichtungszeit_batch

            # C106 - Beschichtungszeit Quantity =((AUFRUNDEN((((((C2-C30)*(C22-1))+(C2-C31))*1000)/C77);0)*C94)/3600)
            beschichtungszeit_quantity = ((math.ceil((((((
                                        printer[self.PrinterValues.buildChamberHeight] - height_offset_first_batch_n_1) * (
                                        min_batch_quantity - 1)) + (
                                        printer[self.PrinterValues.buildChamberHeight] - height_offset_last_batch_n)) * 1000.) / printer[self.PrinterValues.layerThickness])) * printer[self.PrinterValues.coatingTime]) / 3600.)
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["beschichtungszeit_quantity"] = beschichtungszeit_quantity

            # C79 - Druckdauer Batch =C105+C108
            print_duration_batch = beschichtungszeit_batch + belichtungszeit_batch
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["print_duration_batch"] = print_duration_batch

            # C103 - Anzahl an Batches C22
            #anzahl_an_batches = min_batch_quantity

            return print_duration_batch, beschichtungszeit_quantity, min_batch_quantity, theo_max_parts_per_batch
        except Exception as e:
            loggerError.error("Error in calculateCostsForBatches: " + str(e))
            return e, e, e, e

    ##################################################
    def calculateCostsForMaterial(self, groupID, modelID, printerIdx, printer:dict, theo_max_parts_per_batch:int, partVolume:float, partQuantity:int, productComplexity) -> list:
        """
        Calculate the costs for every material

        """
        try:
            totalCostsForEveryMaterial = []
            for material in self.listOfValuesForEveryMaterial: # this assumes that all selected materials are available for the printer, array is only one element long currently
                
                amountOfMaterial = ( (partVolume * printer[self.PrinterValues.fillRate] * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000.)
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["amountOfMaterial"] = amountOfMaterial

                # C41 - material printing cost for the part
                material_cost_printing_part = amountOfMaterial * material[self.MaterialValues.priceOfSpecificMaterial]
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["material_cost_printing_part"] = material_cost_printing_part


                # C43 - material printing cost for the quantity
                material_cost_printing_quantity = material_cost_printing_part * partQuantity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["material_cost_printing_quantity"] = material_cost_printing_quantity

                # C44 - machine material loss for the part
                cost_machine_material_loss_part = material_cost_printing_part * (printer[self.PrinterValues.machineMaterialLoss] / 100)
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_machine_material_loss_part"] = cost_machine_material_loss_part

                # C46 - cost for material loss per quantity
                cost_machine_material_loss_quantity = cost_machine_material_loss_part * partQuantity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_machine_material_loss_quantity"] = cost_machine_material_loss_quantity

                # C59 - support structures part rate
                supportStructuresPartRate = productComplexity*10.

                # C48 - depending on complexity 0 = 0 ; 1 = 10; 2 = 20; 3 = 30
                cost_support_structures_part = material_cost_printing_part * supportStructuresPartRate/100.
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_support_structures_part"] = cost_support_structures_part

                # C50 - cost for support structures per quantity
                cost_support_structures_quantity = cost_support_structures_part * partQuantity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_support_structures_quantity"] = cost_support_structures_quantity

                # C49 - cost for support structures per batch
                cost_support_structures_batch = cost_support_structures_part * theo_max_parts_per_batch
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_support_structures_batch"] = cost_support_structures_batch

                # C42 - material printing cost for one batch
                material_cost_printing_batch = material_cost_printing_part * theo_max_parts_per_batch
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["material_cost_printing_batch"] = material_cost_printing_batch

                # C45 - cost for material loss per batch
                cost_machine_material_loss_batch = cost_machine_material_loss_part * theo_max_parts_per_batch
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_machine_material_loss_batch"] = cost_machine_material_loss_batch

                # C53 - total material cost for the batch
                total_material_cost_batch = material_cost_printing_batch + cost_machine_material_loss_batch + cost_support_structures_batch
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["total_material_cost_batch"] = total_material_cost_batch

                # C52 - total material cost for the part
                total_material_cost_part = material_cost_printing_part + cost_machine_material_loss_part + cost_support_structures_part
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["total_material_cost_part"] = total_material_cost_part

                total_material_cost_quantity = material_cost_printing_quantity + cost_machine_material_loss_quantity + cost_support_structures_quantity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["total_material_cost_quantity"] = total_material_cost_quantity

                totalCostsForEveryMaterial.append( (total_material_cost_part, total_material_cost_quantity, total_material_cost_batch) )
            
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
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"] = {}
            for modelID, model in group[ServiceDetails.models].items():
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID] = {}
                levelOfDetail = model.get(FileObjectContent.levelOfDetail, 1)
                if FileObjectContent.isFile in model and model[FileObjectContent.isFile] == False:
                    partQuantity = model[FileObjectContent.quantity]
                    productComplexity = model[FileContentsAM.complexity]
                    partHeight = model[FileContentsAM.height]
                    partLength = model[FileContentsAM.length]
                    partWidth = model[FileContentsAM.width]
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
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["levelOfDetail"] = levelOfDetail
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["partVolume"] = partVolume
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["partQuantity"] = partQuantity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["productComplexity"] = productComplexity
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["partHeight"] = partHeight
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["partLength"] = partLength
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["partWidth"] = partWidth

                # calculate costs for organization

                # C60 - depends on complexity 0 = 0; 1 = 1; 2 = 2; 3 = 4
                personalEngineeringHours = productComplexity if productComplexity < 3 else 4
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["personalEngineeringHours"] = personalEngineeringHours

                # C62 - cost for personal engineering
                costPersonalEngineering = personalEngineeringHours * self.costRatePersonnelEngineering
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costPersonalEngineering"] = costPersonalEngineering

                # C64 - cost for equipment engineering
                costEquipmentEngineering = self.costRateEquipmentEngineering * personalEngineeringHours + self.fixedCostsEquipmentEngineering
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costEquipmentEngineering"] = costEquipmentEngineering

                # C71 - cost equipment
                costEquipment = costEquipmentEngineering # TODO why should that be?! C71 = C64 in Excel sheet
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costEquipment"] = costEquipment

                totalCostsForEveryPrinter = []
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"] = [{} for _ in range(len(self.listOfValuesForEveryPrinter))]
                for printerIdx, printer in enumerate(self.listOfValuesForEveryPrinter):

                    printingSpeedForMaterialAndPrinter = self.minimalPrintingSpeed
                    # if extrusion printer and build rate is not set, calculate it
                    if printingSpeedForMaterialAndPrinter > printer[self.PrinterValues.maxPrintingSpeed]:
                        printingSpeedForMaterialAndPrinter = printer[self.PrinterValues.maxPrintingSpeed]
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["printingSpeedForMaterialAndPrinter"] = printingSpeedForMaterialAndPrinter

                    buildRateForThisPrinter = 0
                    if printer[self.PrinterValues.technology] == "Material Extrusion":
                        if self.PrinterValues.buildRate not in printer:
                            buildRateForThisPrinter = (printer[self.PrinterValues.nozzleDiameter] / 10. )* (printer[self.PrinterValues.layerThickness] / 10000.) * printingSpeedForMaterialAndPrinter # converted values to cm so that unit is cm^3/h
                        else:
                            buildRateForThisPrinter = printer[self.PrinterValues.buildRate]
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["buildRateForThisPrinter"] = buildRateForThisPrinter

                    # C81 - schichten_part =AUFRUNDEN((C15*1000)/C77;0)
                    schichten_part =  math.ceil((partHeight * 1000) / printer[self.PrinterValues.layerThickness])
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["schichten_part"] = schichten_part

                    # C89 - Flächennutzung der Maschine =AUFRUNDEN(C88*1,25;0) - Flächenfaktormethode nach Rockstroh ca. +25%
                    flaechennutzung_der_maschine = math.ceil(printer[self.PrinterValues.machineSurfaceArea] * 1.25)
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["flaechennutzung_der_maschine"] = flaechennutzung_der_maschine

                    # C91 - Flächennutzungskosten =C89*C90
                    flaechennutzungskosten = flaechennutzung_der_maschine * self.roomCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["flaechennutzungskosten"] = flaechennutzungskosten

                    # 92 - Stundensatz für Flächennutzung - Berechnung des Stundensatzes für die Fläche =(C91/30)/24 #TODO (wieso /30 nicht 60)??
                    stundensatz_fuer_flaechennutzung = (flaechennutzungskosten / 30.) / 24.
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["stundensatz_fuer_flaechennutzung"] = stundensatz_fuer_flaechennutzung

                    # C96 - Kosten Strom pro Stunde =C83*C82
                    kosten_strom_pro_stunde = printer[self.PrinterValues.averagePowerConsumption] * self.powerCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["kosten_strom_pro_stunde"] = kosten_strom_pro_stunde

                    # C68 - cost for personal machine
                    cost_personal_machine = printer[self.PrinterValues.costRatePersonalMachine] * (printer[self.PrinterValues.machineSetUpSimple] + printer[self.PrinterValues.machineSetUpComplex])
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_personal_machine"] = cost_personal_machine

                    # C70 - cost personal pre process
                    cost_personal_pre_process = costPersonalEngineering + cost_personal_machine
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["cost_personal_pre_process"] = cost_personal_pre_process

                    # C72 - cost pre process
                    costPreProcessTotal = cost_personal_pre_process + costEquipment
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costPreProcessTotal"] = costPreProcessTotal

                    # C97 - Allgemeiner Abschreibungssatz =C76
                    amortizationRate = printer[self.PrinterValues.machineHourlyRate]
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["amortizationRate"] = amortizationRate

                    # C98 - Reparatur =C97*C84
                    reparatur = amortizationRate * self.repairCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["reparatur"] = reparatur

                    # C100 - Fläche =C92
                    flaeche = stundensatz_fuer_flaechennutzung
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["flaeche"] = flaeche

                    # C104 - Beschichtungszeit Part =(C81*C94)/3600
                    beschichtungszeit_part = (schichten_part * printer[self.PrinterValues.coatingTime]) / 3600.
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["beschichtungszeit_part"] = beschichtungszeit_part

                    # C107 - Belichtungszeit ein Teil =((C94*C81)/3600)
                    belichtungszeit_ein_teil = (printer[self.PrinterValues.coatingTime]  * schichten_part) / 3600.
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["belichtungszeit_ein_teil"] = belichtungszeit_ein_teil

                    print_duration_batch, beschichtungszeit_quantity, min_batch_quantity, theo_max_parts_per_batch = self.calculateCostsForBatches(groupID, modelID, printerIdx, printer, belichtungszeit_ein_teil, partLength, partHeight, partWidth, partQuantity)

                    listOfCostsForMaterial = self.calculateCostsForMaterial(groupID, modelID, printerIdx, printer, theo_max_parts_per_batch, partVolume, partQuantity, productComplexity)

                    # C109 - Belichtungszeit Quantity =((C94*C81)/3600)*C21
                    belichtungszeit_quantity = ((printer[self.PrinterValues.coatingTime] * schichten_part) / 3600.) * partQuantity
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["belichtungszeit_quantity"] = belichtungszeit_quantity

                    print_duration_part = beschichtungszeit_part + belichtungszeit_ein_teil
                    print_duration_quantity = beschichtungszeit_quantity + belichtungszeit_quantity
                    if printer[self.PrinterValues.technology] == "Powder Bed Fusion":
                        # C78 - Druckdauer Part =C104+C107
                        print_duration_part = beschichtungszeit_part + belichtungszeit_ein_teil
                        self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["print_duration_part"] = print_duration_part

                        # C80 - Druckdauer Quantity =C106+C109
                        print_duration_quantity = beschichtungszeit_quantity + belichtungszeit_quantity
                        self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["print_duration_quantity"] = print_duration_quantity
                    if printer[self.PrinterValues.technology] == "Material Extrusion":
                        # C78 - Druckdauer Part =C104+C107
                        print_duration_part = 2.5 * partVolume * printer[self.PrinterValues.fillRate] / buildRateForThisPrinter # the 2.5 is an empirical value
                        self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["print_duration_part"] = print_duration_part

                        # C80 - Druckdauer Quantity =C106+C109
                        print_duration_quantity = print_duration_part * partQuantity
                        self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["print_duration_quantity"] = print_duration_quantity

                    # C99 - Schutzgas =C87
                    safetyGas = self.safetyGasPerHour
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["safetyGas"] = safetyGas

                    # C102 =SUMME(C96:C100)
                    gesamter_maschinenstundensatz = kosten_strom_pro_stunde + amortizationRate + reparatur + safetyGas + flaeche
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["gesamter_maschinenstundensatz"] = gesamter_maschinenstundensatz

                    # C112 - Maschinenkosten Druckprozess Batch =C79*C102
                    machine_costs_print_process_batch = print_duration_batch * gesamter_maschinenstundensatz
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machine_costs_print_process_batch"] = machine_costs_print_process_batch

                    # C111 - Maschinenkosten Druckprozess Part =C78*C102
                    machine_costs_print_process_part = print_duration_part * gesamter_maschinenstundensatz
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machine_costs_print_process_part"] = machine_costs_print_process_part

                    # C113 - Maschinenkosten Druckprozess Quantity =C80*C102
                    machine_costs_print_process_quantity = print_duration_quantity * gesamter_maschinenstundensatz
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["machine_costs_print_process_quantity"] = machine_costs_print_process_quantity

                    # C114 - Personalkosten Druckprozess =(C22-1)*C68
                    personalkosten_print_process = (min_batch_quantity - 1) * cost_personal_machine + self.personnelCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["personalkosten_print_process"] = personalkosten_print_process

                    costsTotalForPrinterPart = machine_costs_print_process_part + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterPart"] = costsTotalForPrinterPart
                    costsTotalForPrinterQuantity = machine_costs_print_process_quantity + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterQuantity"] = costsTotalForPrinterQuantity
                    costsTotalForPrinterBatch = machine_costs_print_process_batch + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    self.detailedCalculations[ServiceDetails.groups][groupID]["costsPerModel"][modelID]["costsForEveryPrinter"][printerIdx]["costsTotalForPrinterBatch"] = costsTotalForPrinterBatch
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
            self.detailedCalculations[ServiceDetails.groups][groupID]["costsForEveryPostProcessing"] = [{} for _ in range(len(self.listOfValuesForEveryPostProcessing))]
            for postProcessingIdx, postProcessing in enumerate(self.listOfValuesForEveryPostProcessing):
                # C115 - Total costs for post processing
                totalPostProcessingCosts = postProcessing[self.PostProcessingValues.fixedCostsPostProcessing] + postProcessing[self.PostProcessingValues.treatmentCostsPostProcessing]
                self.detailedCalculations[ServiceDetails.groups][groupID]["costsForEveryPostProcessing"][postProcessingIdx]["totalPostProcessingCosts"] = totalPostProcessingCosts

                totalCostsForEveryPostProcessing.append(totalPostProcessingCosts)

            return totalCostsForEveryPostProcessing
        except Exception as e:
            loggerError.error("Error in calculateCostsForPostProcessings: " + str(e))
            return e
    
    ####################################################################################################
    def calculateCosts(self) -> list[tuple[float,float]]|Exception:
        """
        Calculate all costs
        
        """
        try: 
            costsPerGroup = []
            for groupIdx, group in enumerate(self.processObj.serviceDetails[ServiceDetails.groups]):
                self.detailedCalculations[ServiceDetails.groups] = [{} for _ in range(len(self.processObj.serviceDetails[ServiceDetails.groups]))]
                retVal = self.fetchInformation(groupIdx, group)
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
                marginPlattform = 1. + PLATFORM_MARGIN/100.

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
                    

                totalCosts = [(minimumCosts[0]*marginOrganization*marginPlattform, maximumCosts[0]*marginOrganization*marginPlattform), (minimumCosts[1]*marginOrganization*marginPlattform, maximumCosts[1]*marginOrganization*marginPlattform), (minimumCosts[2]*marginOrganization*marginPlattform, maximumCosts[2]*marginOrganization*marginPlattform)]
                for i in range(len(totalCosts)):
                    left, right = totalCosts[i]
                    if numpy.isnan(left) or not numpy.isfinite(left):
                        left = -1.
                    if numpy.isnan(right) or not numpy.isfinite(right):
                        right = -1.
                    totalCosts[i] = (left, right)
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