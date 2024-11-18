"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Cost calculations for this service
"""
import math, logging, numpy

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import *

from ..definitions import *
from ..connections.postgresql import pgKG
from ..connections.filterViaSparql import Filter


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

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
        
    ##################################################
    class PrinterValues(StrEnumExactlyAsDefined):
        """
        Values for every printer
        
        """
        
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
        coatingTime = enum.auto()

    ##################################################
    class MaterialValues(StrEnumExactlyAsDefined):
        """
        Values for every material
        
        """
        
        priceOfSpecificMaterial = enum.auto()
        densityOfSpecificMaterial = enum.auto()
        supportStructuresPartRate = enum.auto()

    ##################################################
    class PostProcessingValues(StrEnumExactlyAsDefined):
        """
        Values for every post processing
        
        """
        
        fixedCostsPostProcessing = enum.auto()
        treatmentCostsPostProcessing = enum.auto()

    ##################################################
    def fetchInformation(self) -> None|Exception:
        """
        Fetch information about everything
        
        """
        try:
            # From Organization
            organization = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=self.additionalArguments["orgaID"])
            if checkIfNestedKeyExists(organization, OrganizationDescription.details, OrganizationDetails.services, SERVICE_NAME) == True:
                orgaParameters = organization[OrganizationDescription.details][OrganizationDetails.services][SERVICE_NAME]

                for entry in orgaParameters:
                    value = entry[ServiceSpecificFields.value]
                    match entry[ServiceSpecificFields.key]:
                        case OrganizationDetailsAM.costRatePersonnelEngineering:
                            self.costRatePersonnelEngineering = value
                        case OrganizationDetailsAM.costRateEquipmentEngineering:
                            self.costRateEquipmentEngineering = value
                        case OrganizationDetailsAM.repairCosts:
                            self.repairCosts = value
                        case OrganizationDetailsAM.safetyGasCosts:
                            self.safetyGasPerHour = value
                        case OrganizationDetailsAM.roomCosts:
                            self.roomCosts = value
                        case OrganizationDetailsAM.powerCosts:
                            self.powerCosts = value
                        case OrganizationDetailsAM.additionalFixedCosts:
                            self.additionalFixedCosts = value
                        case OrganizationDetailsAM.fixedCostsEquipmentEngineering:
                            self.fixedCostsEquipmentEngineering = value
                        case OrganizationDetailsAM.margin:
                            self.organizationMargin = value
                        case OrganizationDetailsAM.personnelCosts:
                            self.personnelCosts = value
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

            # From Printer
            viablePrintersOfTheManufacturer = self.filterObject.getPrintersOfAContractor(self.additionalArguments["orgaID"])
            self.listOfValuesForEveryPrinter = []
            for printer in viablePrintersOfTheManufacturer:
                valuesForThisPrinter = {}
                propertiesOfPrinter = printer[pgKG.NodeDescription.properties]
                for entry in propertiesOfPrinter:
                    value = entry[pgKG.NodePropertyDescription.value]
                    match entry[pgKG.NodePropertyDescription.name]:
                        case NodePropertiesAMPrinter.costRatePersonalMachine:
                            valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine] = value
                        case NodePropertiesAMPrinter.chamberBuildHeight:
                            valuesForThisPrinter[self.PrinterValues.buildChamberHeight] = value
                        case NodePropertiesAMPrinter.chamberBuildLength:
                            valuesForThisPrinter[self.PrinterValues.buildChamberLength] = value
                        case NodePropertiesAMPrinter.chamberBuildWidth:
                            valuesForThisPrinter[self.PrinterValues.buildChamberWidth] = value
                        case NodePropertiesAMPrinter.lossOfMaterial:
                            valuesForThisPrinter[self.PrinterValues.machineMaterialLoss] = value
                        case NodePropertiesAMPrinter.machineBatchDistance:
                            valuesForThisPrinter[self.PrinterValues.machineBatchDistance] = value
                        case NodePropertiesAMPrinter.possibleLayerHeights:
                            valuesForThisPrinter[self.PrinterValues.layerThickness] = value[0]
                        case NodePropertiesAMPrinter.machineSize:
                            valuesForThisPrinter[self.PrinterValues.machineSurfaceArea] = value
                        case NodePropertiesAMPrinter.simpleMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpSimple] = value
                        case NodePropertiesAMPrinter.complexMachineSetUp:
                            valuesForThisPrinter[self.PrinterValues.machineSetUpComplex] = value
                        case NodePropertiesAMPrinter.averagePowerConsumption:
                            valuesForThisPrinter[self.PrinterValues.averagePowerConsumption] = value
                        case NodePropertiesAMPrinter.machineHourlyRate:
                            valuesForThisPrinter[self.PrinterValues.machineHourlyRate] = value
                        case NodePropertiesAMPrinter.coatingTime:
                            valuesForThisPrinter[self.PrinterValues.coatingTime] = value

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
                if NodePropertiesAMPrinter.machineSize not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSurfaceArea] = 1.8
                if NodePropertiesAMPrinter.simpleMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpSimple] = 1
                if NodePropertiesAMPrinter.complexMachineSetUp not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineSetUpComplex] = 2
                if NodePropertiesAMPrinter.averagePowerConsumption not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.averagePowerConsumption] = 5
                if NodePropertiesAMPrinter.machineHourlyRate not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.machineHourlyRate] = 51.80
                if NodePropertiesAMPrinter.coatingTime not in propertiesOfPrinter:
                    valuesForThisPrinter[self.PrinterValues.coatingTime] = 9
                
                self.listOfValuesForEveryPrinter.append(valuesForThisPrinter)

            # From Material
            self.listOfValuesForEveryMaterial = []
            chosenMaterials = self.processObj.serviceDetails[ServiceDetails.materials]
            for materialID in chosenMaterials:
                material = chosenMaterials[materialID]
                valuesForThisMaterial = {}
                valuesForThisMaterial[self.MaterialValues.priceOfSpecificMaterial] = material.get(NodePropertiesAMMaterial.acquisitionCosts, 400)
                valuesForThisMaterial[self.MaterialValues.densityOfSpecificMaterial] = material.get(NodePropertiesAMMaterial.density, 4.43)
                valuesForThisMaterial[self.MaterialValues.supportStructuresPartRate] = material.get(NodePropertiesAMMaterial.supportStructurePartRate, 10)
                self.listOfValuesForEveryMaterial.append(valuesForThisMaterial)

            # From PostProcessing
            self.listOfValuesForEveryPostProcessing = []
            if ServiceDetails.postProcessings in self.processObj.serviceDetails:
                chosenPostProcessings = self.processObj.serviceDetails[ServiceDetails.postProcessings]
                for postProcessingID in chosenPostProcessings:
                    postProcessing = chosenPostProcessings[postProcessingID]
                    valuesForThisPostProcessing = {}
                    valuesForThisPostProcessing[self.PostProcessingValues.fixedCostsPostProcessing] = postProcessing.get(NodePropertiesAMAdditionalRequirement.fixedCosts, 0)
                    valuesForThisPostProcessing[self.PostProcessingValues.treatmentCostsPostProcessing] = postProcessing.get(NodePropertiesAMAdditionalRequirement.treatmentCosts, 0)
                    self.listOfValuesForEveryPostProcessing.append(valuesForThisPostProcessing)
        except Exception as e:
            loggerError.error("Error in fetchInformation: " + str(e))
            return e


    ##################################################
    def calculateCostsForBatches(self, printer:dict, exposureTime:float, partLength:float, partHeight:float, partWidth:float, partQuantity:int) -> tuple:
        """
        Calculate the costs for the batches
        
        """
        try:
            # C09 - Calculation of max. printed parts in z-dimension, batch distance is only between the parts, first layer and last layer of the chamber is fully used
            theo_max_Batch_size_height = math.floor((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) // (partHeight + printer[self.PrinterValues.machineBatchDistance]))
            print("Theo max batch size height: ", theo_max_Batch_size_height)

            # C10 - Calculation of max. printed parts in x-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theo_max_Batch_size_length = math.floor((printer[self.PrinterValues.buildChamberLength] ) // (partLength + printer[self.PrinterValues.machineBatchDistance]))
            print("Theo max batch size length: ", theo_max_Batch_size_length)

            # C11 - Calculation of max. printed parts in y-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
            theo_max_Batch_size_width = math.floor((printer[self.PrinterValues.buildChamberWidth] ) // (partWidth + printer[self.PrinterValues.machineBatchDistance]))
            print("Theo max batch size width: ", theo_max_Batch_size_width)

            # C12 - Calculation of max. printed parts in xy-plain
            theo_max_batch_size_xy = theo_max_Batch_size_length * theo_max_Batch_size_width
            print("Theo max batch size xy: ", theo_max_batch_size_xy)

            # C13 - Calculation of max. printed parts in chamber
            theo_max_parts_per_batch = theo_max_batch_size_xy * theo_max_Batch_size_height
            print("Theo max parts per batch: ", theo_max_parts_per_batch)

            # C18 - Resulting Bounding-Box volume of x,y,z with batch distance in each dimension
            #volume_bounding_box = (self.partHeight + machineBatchDistance) * (partLength + machineBatchDistance) * (partWidth + machineBatchDistance)

            # C22 - How many batches you need at least to print the quanitity
            min_batch_quantity = math.ceil(partQuantity / theo_max_parts_per_batch)
            print("Min batch quantity: ", min_batch_quantity)

            # C23 - Shows how many parts could be printed in the last batch
            all_unused_batch = min_batch_quantity * theo_max_parts_per_batch - partQuantity
            print("All unused batch: ", all_unused_batch)

            # C24 - Shows how many bounding boxes in z-dimension is unused
            unused_batch_size_height = all_unused_batch // theo_max_batch_size_xy
            print("Unused batch size height: ", unused_batch_size_height)

            # C25 - Shows how many bounding boxes in z-dimension is used
            used_batch_size_height = theo_max_Batch_size_height - unused_batch_size_height
            print("Used batch size height: ", used_batch_size_height)

            # C27 - Shows how many bounding boxes in the xy-plain is used
            used_batch_size_xz = (theo_max_Batch_size_length * theo_max_Batch_size_width) if partQuantity % theo_max_batch_size_xy == 0 else partQuantity % theo_max_batch_size_xy
            print("Used batch size xy: ", used_batch_size_xz)

            # C26 - Shows how many bounding boxes in the xy-plain is unused
            unused_batch_size_xz = theo_max_batch_size_xy - used_batch_size_xz
            print("Unused batch size xy: ", unused_batch_size_xz)

            # C28 - Checks if used bounding boxes are the same as the part quantity
            quantity_check = partQuantity == min_batch_quantity * theo_max_Batch_size_height * theo_max_batch_size_xy - unused_batch_size_height * theo_max_batch_size_xy - unused_batch_size_xz
            print("Quantity check: ", quantity_check)

            # C30 - Calculates the summ of all unused heigth of the chamber in mm for all batches excluding batch n
            height_offset_first_batch_n_1 = ((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * theo_max_Batch_size_height) * (min_batch_quantity - 1)
            print("Height offset first batch n-1: ", height_offset_first_batch_n_1)

            # C31 - Calculates unused heigth of the chamber in mm for  batch n
            height_offset_last_batch_n = (printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) - (partHeight + printer[self.PrinterValues.machineBatchDistance]) * used_batch_size_height
            print("Height offset last batch n: ", height_offset_last_batch_n)

            # C32 - Ratio between used chamber height and unused chamber height over all batches
            chamber_height_fillgrade = 1 - ( (height_offset_first_batch_n_1 + height_offset_last_batch_n) / (min_batch_quantity * printer[self.PrinterValues.buildChamberHeight]))
            print("Chamber height fillgrade: ", chamber_height_fillgrade)

            # C108 - Belichtungszeit Batch =C107*C13
            belichtungszeit_batch = exposureTime * theo_max_parts_per_batch
            print("Belichtungszeit batch: ", belichtungszeit_batch)

            # C105 - Beschichtungszeit Batch ==(AUFRUNDEN(((C2*1000)/C77);0)*C94)/3600
            beschichtungszeit_batch = (math.ceil((printer[self.PrinterValues.buildChamberHeight] * 1000.) / printer[self.PrinterValues.layerThickness]) * printer[self.PrinterValues.coatingTime]) / 3600.
            print("Beschichtungszeit batch: ", beschichtungszeit_batch)

            # C106 - Beschichtungszeit Quantity =((AUFRUNDEN((((((C2-C30)*(C22-1))+(C2-C31))*1000)/C77);0)*C94)/3600)
            beschichtungszeit_quantity = ((math.ceil((((((
                                        printer[self.PrinterValues.buildChamberHeight] - height_offset_first_batch_n_1) * (
                                        min_batch_quantity - 1)) + (
                                        printer[self.PrinterValues.buildChamberHeight] - height_offset_last_batch_n)) * 1000.) / printer[self.PrinterValues.layerThickness])) * printer[self.PrinterValues.coatingTime]) / 3600.)
            print("Beschichtungszeit quantity: ", beschichtungszeit_quantity)

            # C79 - Druckdauer Batch =C105+C108
            print_duration_batch = beschichtungszeit_batch + belichtungszeit_batch
            print("Print duration batch: ", print_duration_batch)


            # C103 - Anzahl an Batches C22
            #anzahl_an_batches = min_batch_quantity

            return print_duration_batch, beschichtungszeit_quantity, min_batch_quantity, theo_max_parts_per_batch
        except Exception as e:
            loggerError.error("Error in calculateCostsForBatches: " + str(e))
            return e, e, e, e

    ##################################################
    def calculateCostsForMaterial(self, printer:dict, theo_max_parts_per_batch:int, partVolume:float, partQuantity:int, productComplexity) -> list:
        """
        Calculate the costs for every material

        """
        try:
            totalCostsForEveryMaterial = []
            for material in self.listOfValuesForEveryMaterial: # this assumes that all selected materials are available for the printer
                # C41 - material printing cost for the part
                material_cost_printing_part = ( (partVolume * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000.) * material[self.MaterialValues.priceOfSpecificMaterial]
                print("Material cost printing part: ", material_cost_printing_part)

                # C43 - material printing cost for the quantity
                material_cost_printing_quantity = material_cost_printing_part * partQuantity
                print("Material cost printing quantity: ", material_cost_printing_quantity)

                # C44 - machine material loss for the part
                cost_machine_material_loss_part = ((( partVolume * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000.) * material[self.MaterialValues.priceOfSpecificMaterial]) * (printer[self.PrinterValues.machineMaterialLoss] / 100)
                print("Cost machine material loss part: ", cost_machine_material_loss_part)

                # C46 - cost for material loss per quantity
                cost_machine_material_loss_quantity = cost_machine_material_loss_part * partQuantity
                print("Cost machine material loss quantity: ", cost_machine_material_loss_quantity)

                # C48 - depending on complexity 0 = 0 ; 1 = 10; 2 = 20; 3 = 30
                cost_support_structures_part = material[self.MaterialValues.supportStructuresPartRate] * productComplexity
                print("Cost support structures part: ", cost_support_structures_part)

                # C49 - cost for support structures per batch
                cost_support_structures_batch = cost_support_structures_part * theo_max_parts_per_batch
                print("Cost support structures batch: ", cost_support_structures_batch)

                # C50 - cost for support structures per quantity
                cost_support_structures_quantity = cost_support_structures_part * partQuantity
                print("Cost support structures quantity: ", cost_support_structures_quantity)

                # C42 - material printing cost for one batch
                material_cost_printing_batch = material_cost_printing_part * theo_max_parts_per_batch
                print("Material cost printing batch: ", material_cost_printing_batch)

                # C45 - cost for material loss per batch
                cost_machine_material_loss_batch = cost_machine_material_loss_part * theo_max_parts_per_batch
                print("Cost machine material loss batch: ", cost_machine_material_loss_batch)

                # C53 - total material cost for the batch
                total_material_cost_batch = material_cost_printing_batch + cost_machine_material_loss_batch + cost_support_structures_batch
                print("Total material cost batch: ", total_material_cost_batch)

                # C52 - total material cost for the part
                total_material_cost_part = material_cost_printing_part + cost_machine_material_loss_part + cost_support_structures_part
                print("Total material cost part: ", total_material_cost_part)

                total_material_cost_quantity = material_cost_printing_quantity + cost_machine_material_loss_quantity + cost_support_structures_quantity
                print("Total material cost quantity: ", total_material_cost_quantity)

                totalCostsForEveryMaterial.append( (total_material_cost_part, total_material_cost_quantity, total_material_cost_batch) )
            
            return totalCostsForEveryMaterial
        except Exception as e:
            loggerError.error("Error in calculateCostsForMaterial: " + str(e))
            return e

    ##################################################
    def calculateCostsForPrinter(self) -> dict[list[tuple]]:
        """
        Calculate the costs for every printer

        """
        try:
            printerCostsPerModel = {}
            # for all models
            for modelID, model in self.processObj.serviceDetails[ServiceDetails.models].items():
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
                    if ServiceDetails.calculations in self.processObj.serviceDetails:
                        partHeight = self.processObj.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._3]
                        partLength = self.processObj.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._2]
                        partWidth = self.processObj.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._1]
                        volumeOfModel = self.processObj.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.volume]
                        boundingBoxVolume = self.processObj.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbVolume]
                        machineEpsilon = 7./3 - 4./3 - 1 # Nevermind that, it just calculates the machine epsion to avoid division by zero
                        productComplexity = round( (1. - volumeOfModel / (boundingBoxVolume + machineEpsilon)) * 4.) # scale to [0,4], then assign nearest integer
                        partVolume = volumeOfModel / 1000. # to cm³
                    else:
                        loggerError.error("No calculations available for model")
                print(f"Part volume: {partVolume}, part quantity: {partQuantity}, product complexity: {productComplexity}, part height: {partHeight}, part length: {partLength}, part width: {partWidth}")

                # calculate costs for organization

                # C60 - depends on complexity 0 = 0; 1 = 1; 2 = 2; 3 = 4
                personalEngineeringHours = productComplexity if productComplexity < 3 else 4
                print("Personal engineering hours: ", personalEngineeringHours)

                # C62 - cost for personal engineering
                costPersonalEngineering = personalEngineeringHours * self.costRatePersonnelEngineering
                print("Cost personal engineering: ", costPersonalEngineering)

                # C64 - cost for equipment engineering
                costEquipmentEngineering = self.costRateEquipmentEngineering * personalEngineeringHours + self.fixedCostsEquipmentEngineering
                print("Cost equipment engineering: ", costEquipmentEngineering)

                # C71 - cost equipment
                costEquipment = costEquipmentEngineering # TODO why should that be?! C71 = C64 in Excel sheet
                print("Cost equipment: ", costEquipment)

                totalCostsForEveryPrinter = []
                for printer in self.listOfValuesForEveryPrinter:
                    
                    # C81 - schichten_part =AUFRUNDEN((C15*1000)/C77;0)
                    schichten_part =  math.ceil((partHeight * 1000) / printer[self.PrinterValues.layerThickness])
                    print("Schichten part: ", schichten_part)

                    # C89 - Flächennutzung der Maschine =AUFRUNDEN(C88*1,25;0) - Flächenfaktormethode nach Rockstroh ca. +25%
                    flaechennutzung_der_maschine = math.ceil(printer[self.PrinterValues.machineSurfaceArea] * 1.25)
                    print("Flächennutzung der Maschine: ", flaechennutzung_der_maschine)

                    # C91 - Flächennutzungskosten =C89*C90
                    flaechennutzungskosten = flaechennutzung_der_maschine * self.roomCosts
                    print("Flächennutzungskosten: ", flaechennutzungskosten)

                    # 92 - Stundensatz für Flächennutzung - Berechnung des Stundensatzes für die Fläche =(C91/30)/24 #TODO (wieso /30 nicht 60)??
                    stundensatz_fuer_flaechennutzung = (flaechennutzungskosten / 30.) / 24.
                    print("Stundensatz für Flächennutzung: ", stundensatz_fuer_flaechennutzung)

                    # C96 - Kosten Strom pro Stunde =C83*C82
                    kosten_strom_pro_stunde = printer[self.PrinterValues.averagePowerConsumption] * self.powerCosts
                    print("Kosten Strom pro Stunde: ", kosten_strom_pro_stunde)

                    # C68 - cost for personal machine
                    cost_personal_machine = printer[self.PrinterValues.costRatePersonalMachine] * (printer[self.PrinterValues.machineSetUpSimple] + printer[self.PrinterValues.machineSetUpComplex])
                    print("Cost personal machine: ", cost_personal_machine)

                    # C70 - cost personal pre process
                    cost_personal_pre_process = costPersonalEngineering + cost_personal_machine
                    print("Cost personal pre process: ", cost_personal_pre_process)

                    # C72 - cost pre process
                    costPreProcessTotal = cost_personal_pre_process + costEquipment
                    print("Cost pre process total: ", costPreProcessTotal)

                    # C97 - Allgemeiner Abschreibungssatz =C76
                    amortizationRate = printer[self.PrinterValues.machineHourlyRate]
                    print("Amortization rate: ", amortizationRate)

                    # C98 - Reparatur =C97*C84
                    reparatur = amortizationRate * self.repairCosts
                    print("Reparatur: ", reparatur)

                    # C100 - Fläche =C92
                    flaeche = stundensatz_fuer_flaechennutzung
                    print("Fläche: ", flaeche)

                    # C104 - Beschichtungszeit Part =(C81*C94)/3600
                    beschichtungszeit_part = (schichten_part * printer[self.PrinterValues.coatingTime]) / 3600.
                    print("Beschichtungszeit part: ", beschichtungszeit_part)

                    # C107 - Belichtungszeit ein Teil =((C94*C81)/3600)
                    belichtungszeit_ein_teil = (printer[self.PrinterValues.coatingTime]  * schichten_part) / 3600.
                    print("Belichtungszeit ein Teil: ", belichtungszeit_ein_teil)

                    print_duration_batch, beschichtungszeit_quantity, min_batch_quantity, theo_max_parts_per_batch = self.calculateCostsForBatches(printer, belichtungszeit_ein_teil, partLength, partHeight, partWidth, partQuantity)

                    # C109 - Belichtungszeit Quantity =((C94*C81)/3600)*C21
                    belichtungszeit_quantity = ((printer[self.PrinterValues.coatingTime] * schichten_part) / 3600.) * partQuantity
                    print("Belichtungszeit quantity: ", belichtungszeit_quantity)

                    # C78 - Druckdauer Part =C104+C107
                    print_duration_part = beschichtungszeit_part + belichtungszeit_ein_teil
                    print("Print duration part: ", print_duration_part)

                    # C80 - Druckdauer Quantity =C106+C109
                    print_duration_quantity = beschichtungszeit_quantity + belichtungszeit_quantity
                    print("Print duration quantity: ", print_duration_quantity)

                    # C99 - Schutzgas =C87
                    safetyGas = self.safetyGasPerHour * print_duration_quantity
                    print("Schutzgas: ", safetyGas)

                    # C102 =SUMME(C96:C100)
                    gesamter_maschinenstundensatz = kosten_strom_pro_stunde + amortizationRate + reparatur + safetyGas + flaeche
                    print("Gesamter Maschinenstundensatz: ", gesamter_maschinenstundensatz)

                    # C112 - Maschinenkosten Druckprozess Batch =C79*C102
                    machine_costs_print_process_batch = print_duration_batch * gesamter_maschinenstundensatz
                    print("Maschinenkosten Druckprozess Batch: ", machine_costs_print_process_batch)

                    # C111 - Maschinenkosten Druckprozess Part =C78*C102
                    machine_costs_print_process_part = print_duration_part * gesamter_maschinenstundensatz
                    print("Maschinenkosten Druckprozess Part: ", machine_costs_print_process_part)

                    # C113 - Maschinenkosten Druckprozess Quantity =C80*C102
                    machine_costs_print_process_quantity = print_duration_quantity * gesamter_maschinenstundensatz
                    print("Maschinenkosten Druckprozess Quantity: ", machine_costs_print_process_quantity)

                    # C114 - Personalkosten Druckprozess =(C22-1)*C68
                    personalkosten_print_process = (min_batch_quantity - 1) * cost_personal_machine + self.personnelCosts
                    print("Personalkosten Druckprozess: ", personalkosten_print_process)

                    listOfCostsForMaterial = self.calculateCostsForMaterial(printer, theo_max_parts_per_batch, partVolume, partQuantity, productComplexity)

                    costsTotalForPrinterPart = machine_costs_print_process_part + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    print("Costs total for printer part: ", costsTotalForPrinterPart)
                    costsTotalForPrinterQuantity = machine_costs_print_process_quantity + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    print("Costs total for printer quantity: ", costsTotalForPrinterQuantity)
                    costsTotalForPrinterBatch = machine_costs_print_process_batch + personalkosten_print_process + costPreProcessTotal + self.additionalFixedCosts
                    print("Costs total for printer batch: ", costsTotalForPrinterBatch)
                    # TODO save results in a useful datastructure
                    totalCostsForEveryPrinter.append((costsTotalForPrinterPart, costsTotalForPrinterQuantity, costsTotalForPrinterBatch, listOfCostsForMaterial))
                
                printerCostsPerModel[model[FileObjectContent.id]] = totalCostsForEveryPrinter
            
            return printerCostsPerModel
        except Exception as e:
            loggerError.error("Error in calculateCostsForPrinter: " + str(e))
            return e
    ####################################################################################################

    ##################################################
    def calculateCostsForPostProcessings(self) -> list[float]:
        """
        Calculate the costs for the post processings

        """
        try:
            totalCostsForEveryPostProcessing = []
            for postProcessing in self.listOfValuesForEveryPostProcessing:
                # C115 - Total costs for post processing
                totalPostProcessingCosts = postProcessing[self.PostProcessingValues.fixedCostsPostProcessing] + postProcessing[self.PostProcessingValues.treatmentCostsPostProcessing]
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
            retVal = self.fetchInformation()
            if retVal is not None:
                raise retVal
            printerCostDict = self.calculateCostsForPrinter()
            if isinstance(printerCostDict, Exception):
                raise printerCostDict
            postProcessingCostList = self.calculateCostsForPostProcessings()
            if isinstance(postProcessingCostList, Exception):
                raise postProcessingCostList
            
            postProcessingsCosts = numpy.sum(postProcessingCostList)
            marginOrganization = 1. + self.organizationMargin/100.
            marginPlattform = 1. + PLATFORM_MARGIN/100.

            maximumCosts = [0., 0., 0.] # part, quantity, batch
            minimumCosts = [float("inf"), float("inf"), float("inf")]
            maximumCostsPerFile = {}
            minimumCostsPerFile = {}
            for fileID , printerCostList in printerCostDict.items():
                maximumCostsThisFile = [0., 0., 0.] # part, quantity, batch
                minimumCostsThisFile = [float("inf"), float("inf"), float("inf")]
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
            return totalCosts
        except Exception as e:
            loggerError.error("Error in calculateCosts: " + str(e))
            return e