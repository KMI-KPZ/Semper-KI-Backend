"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Cost calculations for this service
"""
import math, logging

from Generic_Backend.code_General.definitions import *

from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import *

from ..definitions import *
from ..connections.postgresql import pgKG

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
##################################################
class Costs():
    """
    Calculate all costs associated with the additive manufacturing process
    
    """

    def __init__(self, process:ProcessInterface|Process, additionalArguments:dict, modelID:str=""):
        """
        Gather input variables

        """
        self.levelOfDetail = process.processDetails[GeneralInputParameters.levelOfDetail]
        if ProcessDetails.inputParametersNoModel in process.processDetails and modelID == "":
            self.partQuantity = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.quantity]
            self.productComplexity = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.complexity]
            self.partHeight = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.partHeight]
            self.partLength = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.partLength]
            self.partWidth = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.partWidth]
            if InputParametersNoModel.partVolume not in process.processDetails[ProcessDetails.inputParametersNoModel]:
                self.partVolume = self.partHeight * self.partLength * self.partWidth
            else:
                self.partVolume = process.processDetails[ProcessDetails.inputParametersNoModel][InputParametersNoModel.partVolume]
        else:
            model = process.files[modelID]
            self.partQuantity = model[FileObjectContent.quantity]

            self.productComplexity = 1
            if ServiceDetails.calculations in process.serviceDetails:
                self.partHeight = process.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._3]
                self.partLength = process.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._2]
                self.partWidth = process.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._1]
                volumeOfModel = process.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.volume]
                boundingBoxVolume = process.serviceDetails[ServiceDetails.calculations][modelID][Calculations.measurements][Measurements.mbbVolume]
                self.productComplexity = round( (1. - volumeOfModel / boundingBoxVolume) * 4.) # scale to [0,4], then assign nearest integer
                self.partVolume = volumeOfModel
            else:
                loggerError.error("No calculations available for model")
        
        self.fetchInformation(process, additionalArguments)

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
    def fetchInformation(self, process:ProcessInterface|Process, additionalArguments:dict):
        """
        Fetch information about everything
        
        """
        # From Organization
        orgaParameters = additionalArguments["organizationParameters"]
        self.costRatePersonnelEngineering = orgaParameters[OrganizationDetailsAM.costRatePersonnelEngineering]
        self.costRateEquipmentEngineering = orgaParameters[OrganizationDetailsAM.costRateEquipmentEngineering]
        self.repairCosts = orgaParameters[OrganizationDetailsAM.repairCosts]
        self.safetyGasPerHour = orgaParameters[OrganizationDetailsAM.safetyGasCosts]
        self.costEquipmentEngineering = orgaParameters[OrganizationDetailsAM.costRateEquipmentEngineering]
        self.roomCosts = orgaParameters[OrganizationDetailsAM.roomCosts]
        self.powerCosts = orgaParameters[OrganizationDetailsAM.powerCosts]

        # From Printer
        calculatedValuesForPrinter = [self.partWidth, self.partLength, self.partHeight]
        viablePrintersOfTheManufacturer = pgKG.LogicAM.getPrintersOfSpecificManufacturer(calculatedValuesForPrinter, additionalArguments["orgaID"])
        self.listOfValuesForEveryPrinter = []
        for printer in viablePrintersOfTheManufacturer:
            valuesForThisPrinter = {}
            valuesForThisPrinter[self.PrinterValues.costRatePersonalMachine] = printer[NodePropertiesAMPrinter.costRatePersonalMachine]
            valuesForThisPrinter[self.PrinterValues.buildChamberHeight] = printer[NodePropertiesAMPrinter.chamberBuildHeight]
            valuesForThisPrinter[self.PrinterValues.buildChamberLength] = printer[NodePropertiesAMPrinter.chamberBuildLength]
            valuesForThisPrinter[self.PrinterValues.buildChamberWidth] = printer[NodePropertiesAMPrinter.chamberBuildWidth]
            valuesForThisPrinter[self.PrinterValues.machineMaterialLoss] = printer[NodePropertiesAMPrinter.lossOfMaterial]
            valuesForThisPrinter[self.PrinterValues.machineBatchDistance] = printer[NodePropertiesAMPrinter.machineBatchDistance]
            valuesForThisPrinter[self.PrinterValues.layerThickness] = printer[NodePropertiesAMPrinter.possibleLayerHeights][0] # TODO self.levelOfDetail
            valuesForThisPrinter[self.PrinterValues.machineSurfaceArea] = printer[NodePropertiesAMPrinter.machineSize]
            valuesForThisPrinter[self.PrinterValues.machineSetUpSimple] = printer[NodePropertiesAMPrinter.simpleMachineSetUp]
            valuesForThisPrinter[self.PrinterValues.machineSetUpComplex] = printer[NodePropertiesAMPrinter.complexMachineSetUp]
            valuesForThisPrinter[self.PrinterValues.averagePowerConsumption] = printer[NodePropertiesAMPrinter.averagePowerConsumption]
            valuesForThisPrinter[self.PrinterValues.machineHourlyRate] = printer[NodePropertiesAMPrinter.machineHourlyRate]
            valuesForThisPrinter[self.PrinterValues.coatingTime] = printer[NodePropertiesAMPrinter.coatingTime]
            self.listOfValuesForEveryPrinter.append(valuesForThisPrinter)

        # From Material
        self.listOfValuesForEveryMaterial = []
        chosenMaterials = process.serviceDetails[ServiceDetails.materials]
        for materialID in chosenMaterials:
            material = chosenMaterials[materialID]
            valuesForThisMaterial = {}
            valuesForThisMaterial[self.MaterialValues.priceOfSpecificMaterial] = material[NodePropertiesAMMaterial.acquisitionCosts]
            valuesForThisMaterial[self.MaterialValues.densityOfSpecificMaterial] = material[NodePropertiesAMMaterial.density]
            valuesForThisMaterial[self.MaterialValues.supportStructuresPartRate] = material[NodePropertiesAMMaterial.supportStructurePartRate]
            self.listOfValuesForEveryMaterial.append(valuesForThisMaterial)

        # From PostProcessing
        self.listOfValuesForEveryPostProcessing = []
        if ServiceDetails.postProcessings in process.serviceDetails:
            chosenPostProcessings = process.serviceDetails[ServiceDetails.postProcessings]
            for postProcessingID in chosenPostProcessings:
                postProcessing = chosenPostProcessings[postProcessingID]
                valuesForThisPostProcessing = {}
                valuesForThisPostProcessing[self.PostProcessingValues.fixedCostsPostProcessing] = postProcessing[NodePropertiesAMAdditionalRequirement.fixedCosts]
                valuesForThisPostProcessing[self.PostProcessingValues.treatmentCostsPostProcessing] = postProcessing[NodePropertiesAMAdditionalRequirement.treatmentCosts]
                self.listOfValuesForEveryPostProcessing.append(valuesForThisPostProcessing)
        

    ##################################################
    def calculateCostsForOrganization(self):
        """
        Calculate the costs for the organization
        
        """
        # C60 - depends on complexity 0 = 0; 1 = 1; 2 = 2; 3 = 4
        self.personalEngineeringHours = self.productComplexity if self.productComplexity < 3 else 4

        # C62 - cost for personal engineering
        self.costPersonalEngineering = self.personalEngineeringHours * self.costRatePersonnelEngineering

        # C64 - cost for equipment engineering
        self.costEquipmentEngineering = self.costRateEquipmentEngineering * self.personalEngineeringHours

        # C71 - cost equipment
        self.costEquipment = self.costEquipmentEngineering # TODO why should that be?! C71 = C64 in Excel sheet


    ##################################################
    def calculateCostsForBatches(self, printer:dict, totalMachineCosts:float, exposureTime:float):
        """
        Calculate the costs for the batches
        
        """
        # C09 - Calculation of max. printed parts in z-dimension, batch distance is only between the parts, first layer and last layer of the chamber is fully used
        theo_max_Batch_size_height = math.floor((printer[self.PrinterValues.buildChamberHeight] + printer[self.PrinterValues.machineBatchDistance]) // (self.partHeight + printer[self.PrinterValues.machineBatchDistance]))

        # C10 - Calculation of max. printed parts in x-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
        theo_max_Batch_size_length = math.floor((printer[self.PrinterValues.buildChamberLength] ) // (self.partLength + printer[self.PrinterValues.machineBatchDistance]))

        # C11 - Calculation of max. printed parts in y-dimension, batch distance is  between everything, first layer and last layer of the chamber isnt fully used
        theo_max_Batch_size_width = math.floor((printer[self.PrinterValues.buildChamberWidth] ) // (self.partWidth + printer[self.PrinterValues.machineBatchDistance]))

        # C12 - Calculation of max. printed parts in xy-plain
        theo_max_batch_size_xy = theo_max_Batch_size_length * theo_max_Batch_size_width

        # C13 - Calculation of max. printed parts in chamber
        theo_max_parts_per_batch = theo_max_batch_size_xy * theo_max_Batch_size_height

        # C18 - Resulting Bounding-Box volume of x,y,z with batch distance in each dimension
        #volume_bounding_box = (self.partHeight + machineBatchDistance) * (partLength + machineBatchDistance) * (partWidth + machineBatchDistance)

        # C22 - How many batches you need at least to print the quanitity
        min_batch_quantity = math.ceil(self.partQuantity / theo_max_parts_per_batch)

        # C23 - Shows how many parts could be printed in the last batch
        all_unused_batch = min_batch_quantity * theo_max_parts_per_batch - self.partQuantity

        # C24 - Shows how many bounding boxes in z-dimension is unused
        unused_batch_size_height = all_unused_batch // theo_max_batch_size_xy

        # C25 - Shows how many bounding boxes in z-dimension is used
        used_batch_size_height = theo_max_Batch_size_height - unused_batch_size_height

        # C27 - Shows how many bounding boxes in the xy-plain is used
        used_batch_size_xz = (theo_max_Batch_size_length * theo_max_Batch_size_width) if self.partQuantity % theo_max_batch_size_xy == 0 else self.partQuantity % theo_max_batch_size_xy

        # C26 - Shows how many bounding boxes in the xy-plain is unused
        unused_batch_size_xz = theo_max_batch_size_xy - used_batch_size_xz

        # C28 - Checks if used bounding boxes are the same as the part quantity
        quantity_check = self.partQuantity == min_batch_quantity * theo_max_Batch_size_height * theo_max_batch_size_xy - unused_batch_size_height * theo_max_batch_size_xy - unused_batch_size_xz
        print("Quantity check: ", quantity_check)

        # C30 - Calculates the summ of all unused heigth of the chamber in mm for all batches excluding batch n
        height_offset_first_batch_n_1 = ((self.partHeight + printer[self.PrinterValues.machineBatchDistance]) - (self.partHeight + printer[self.PrinterValues.machineBatchDistance]) * theo_max_Batch_size_height) * (min_batch_quantity - 1)

        # C31 - Calculates unused heigth of the chamber in mm for  batch n
        height_offset_last_batch_n = (self.partHeight + printer[self.PrinterValues.machineBatchDistance]) - (self.partHeight + printer[self.PrinterValues.machineBatchDistance]) * used_batch_size_height

        # C32 - Ratio between used chamber height and unused chamber height over all batches
        chamber_height_fillgrade = 1 - ( (height_offset_first_batch_n_1 + height_offset_last_batch_n) / (min_batch_quantity * printer[self.PrinterValues.buildChamberHeight]))

        # C108 - Belichtungszeit Batch =C107*C13
        belichtungszeit_batch = exposureTime * theo_max_parts_per_batch

        # C105 - Beschichtungszeit Batch ==(AUFRUNDEN(((C2*1000)/C77);0)*C94)/3600
        beschichtungszeit_batch = (math.ceil((printer[self.PrinterValues.buildChamberHeight] * 1000) / printer[self.PrinterValues.layerThickness]) * printer[self.PrinterValues.coatingTime]) / 3600.

        # C79 - Druckdauer Batch =C105+C108
        print_duration_batch = beschichtungszeit_batch + belichtungszeit_batch

        # C112 - Maschinenkosten Druckprozess Batch =C79*C102
        machine_costs_print_process_batch = print_duration_batch * totalMachineCosts

        # C103 - Anzahl an Batches C22
        anzahl_an_batches = min_batch_quantity

        return machine_costs_print_process_batch, anzahl_an_batches, min_batch_quantity, theo_max_parts_per_batch

    ##################################################
    def calculateCostsForMaterial(self, printer:dict, theo_max_parts_per_batch:int):
        """
        
        """
        totalCostsForEveryMaterial = []
        for material in self.listOfValuesForEveryMaterial:
            # C41 - material printing cost for the part
            material_cost_printing_part = ( (self.partVolume * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000) * material[self.MaterialValues.priceOfSpecificMaterial]

            # C43 - material printing cost for the quantity
            material_cost_printing_quantity = material_cost_printing_part * self.partQuantity

            # C44 - machine material loss for the part
            cost_machine_material_loss_part = ((( self.partVolume * material[self.MaterialValues.densityOfSpecificMaterial]) / 1000) * material[self.MaterialValues.priceOfSpecificMaterial]) * (printer[self.PrinterValues.machineMaterialLoss] / 100)

            # C46 - cost for material loss per quantity
            cost_machine_material_loss_quantity = cost_machine_material_loss_part * self.partQuantity

            # C48 - depending on complexity 0 = 0 ; 1 = 10; 2 = 20; 3 = 30
            cost_support_structures_part = material[self.MaterialValues.supportStructuresPartRate] * self.productComplexity

            # C49 - cost for support structures per batch
            cost_support_structures_batch = cost_support_structures_part * theo_max_parts_per_batch

            # C50 - cost for support structures per quantity
            cost_support_structures_quantity = cost_support_structures_part * self.partQuantity

            
            # C42 - material printing cost for one batch
            material_cost_printing_batch = material_cost_printing_part * theo_max_parts_per_batch

            # C45 - cost for material loss per batch
            cost_machine_material_loss_batch = cost_machine_material_loss_part * theo_max_parts_per_batch

            # C53 - total material cost for the batch
            total_material_cost_batch = material_cost_printing_batch + cost_machine_material_loss_batch + cost_support_structures_batch

            # C52 - total material cost for the part
            total_material_cost_part = material_cost_printing_part + cost_machine_material_loss_part + cost_support_structures_part

            total_material_cost_quantity = material_cost_printing_quantity + cost_machine_material_loss_quantity + cost_support_structures_quantity
            
            totalCostsForEveryMaterial.append( (total_material_cost_part, total_material_cost_quantity, total_material_cost_batch) )
        
        return totalCostsForEveryMaterial

    ##################################################
    def calculateCostsForPrinter(self):
        """
        Calculate the costs for every printer

        """
        totalCostsForEveryPrinter = []
        for printer in self.listOfValuesForEveryPrinter:
            
            # C81 - schichten_part =AUFRUNDEN((C15*1000)/C77;0)
            schichten_part =  math.ceil((self.partHeight * 1000) / printer[self.PrinterValues.layerThickness])

            # C89 - Flächennutzung der Maschine =AUFRUNDEN(C88*1,25;0) - Flächenfaktormethode nach Rockstroh ca. +25%
            flaechennutzung_der_maschine = math.ceil(printer[self.PrinterValues.machineSurfaceArea] * 1.25)

            # C91 - Flächennutzungskosten =C89*C90
            flaechennutzungskosten = flaechennutzung_der_maschine * self.roomCosts

            # 92 - Stundensatz für Flächennutzung - Berechnung des Stundensatzes für die Fläche =(C91/30)/24 #TODO (wieso /30 nicht 60)??
            stundensatz_fuer_flaechennutzung = (flaechennutzungskosten / 30.) / 24.

            # C96 - Kosten Strom pro Stunde =C83*C82
            kosten_strom_pro_stunde = printer[self.PrinterValues.averagePowerConsumption] * self.powerCosts

            # C68 - cost for personal machine
            cost_personal_machine = printer[self.PrinterValues.costRatePersonalMachine] * (printer[self.PrinterValues.machineSetUpSimple] + printer[self.PrinterValues.machineSetUpComplex])

            # C72 - cost pre process
            costPreProcessTotal = cost_personal_pre_process + self.costEquipment

            # C70 - cost personal pre process
            cost_personal_pre_process = self.costPersonalEngineering + cost_personal_machine

            # C97 - Allgemeiner Abschreibungssatz =C76
            amortizationRate = printer[self.PrinterValues.machineHourlyRate]

            # C98 - Reparatur =C97*C84
            reparatur = amortizationRate * self.repairCosts

            # C100 - Fläche =C92
            flaeche = stundensatz_fuer_flaechennutzung

            # C102 =SUMME(C96:C100)
            gesamter_maschinenstundensatz = kosten_strom_pro_stunde + amortizationRate + reparatur + safetyGas + flaeche

            # C104 - Beschichtungszeit Part =(C81*C94)/3600
            beschichtungszeit_part = (schichten_part * printer[self.PrinterValues.coatingTime]) / 3600.

            # C107 - Belichtungszeit ein Teil =((C94*C81)/3600)
            belichtungszeit_ein_teil = (beschichtungszeit_part * schichten_part) / 3600.

            machine_costs_print_process_batch, anzahl_an_batches, min_batch_quantity, theo_max_parts_per_batch = self.calculateCostsForBatches(printer, gesamter_maschinenstundensatz, belichtungszeit_ein_teil)

            # C106 - Beschichtungszeit Quantity =((AUFRUNDEN((((((C2-C30)*(C22-1))+(C2-C31))*1000)/C77);0)*C94)/3600)
            beschichtungszeit_quantity = ((math.ceil((((((
                                                                    printer[self.PrinterValues.buildChamberHeight] - self.height_offset_first_batch_n_1) * (
                                                                    min_batch_quantity - 1)) + (
                                                                    printer[self.PrinterValues.buildChamberHeight] - self.height_offset_last_batch_n)) * 1000) / printer[self.PrinterValues.layerThickness])) * printer[self.PrinterValues.coatingTime]) / 3600.)
            

            # C109 - Belichtungszeit Quantity =((C94*C81)/3600)*C21
            belichtungszeit_quantity = ((printer[self.PrinterValues.coatingTime] * schichten_part) / 3600.) * self.partQuantity

            # C78 - Druckdauer Part =C104+C107
            print_duration_part = beschichtungszeit_part + belichtungszeit_ein_teil

            # C80 - Druckdauer Quantity =C106+C109
            print_duration_quantity = beschichtungszeit_quantity + belichtungszeit_quantity

            # C99 - Schutzgas =C87
            safetyGas = self.safetyGasPerHour * print_duration_quantity

            # C111 - Maschinenkosten Druckprozess Part =C78*C102
            machine_costs_print_process_part = print_duration_part * gesamter_maschinenstundensatz

            # C113 - Maschinenkosten Druckprozess Quantity =C80*C102
            machine_costs_print_process_quantity = print_duration_quantity * machine_costs_print_process_part

            # C114 - Personalkosten Druckprozess =(C22-1)*C68
            personalkosten_print_process = (min_batch_quantity - 1) * cost_personal_machine

            listOfCostsForMaterial = self.calculateCostsForMaterial(printer, theo_max_parts_per_batch)
            # TODO calculate max and min for all variants (part, quantity, batch)

            costsTotalForPrinterPart = machine_costs_print_process_part + personalkosten_print_process + costPreProcessTotal
            costsTotalForPrinterQuantity = machine_costs_print_process_quantity + personalkosten_print_process + costPreProcessTotal
            costsTotalForPrinterBatch = machine_costs_print_process_batch + personalkosten_print_process + costPreProcessTotal
            
            # TODO save results in a useful datastructure
            totalCostsForEveryPrinter.append((costsTotalForPrinterPart, costsTotalForPrinterQuantity, costsTotalForPrinterBatch))
        
        return totalCostsForEveryPrinter
    ####################################################################################################

    
    ####################################################################################################

    ##################################################
    def calculateCostsForPostProcessings(self):
        """
        
        """
        totalCostsForEveryPostProcessing = []
        for postProcessing in self.listOfValuesForEveryPostProcessing:
            # C115 - Total costs for post processing
            totalPostProcessingCosts = postProcessing[self.PostProcessingValues.fixedCostsPostProcessing] + postProcessing[self.PostProcessingValues.treatmentCostsPostProcessing]
            totalCostsForEveryPostProcessing.append(totalPostProcessingCosts)

        return totalCostsForEveryPostProcessing
    
    ####################################################################################################
    def calculateCosts(self):
        """
        Calculate all costs
        
        """
        self.calculateCostsForOrganization()
        self.calculateCostsForPrinter()
        self.calculateCostsForPostProcessings()

        
        return totalCosts