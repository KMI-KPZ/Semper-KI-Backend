"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic for FEM analysis
"""
from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from code_SemperKI.logics.filesLogics import getFileReadableStream
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process
from code_SemperKI.definitions import ProcessDetails

from ..tasks.femSimulationTask import run_FEM_test
from ..definitions import *

##################################################
def startFEMAnalysis(session, processObj:Process) -> dict|Exception: 
    """
    Start the FEM Analysis on eligable models and materials
    
    """
    try:
        resultDict = {ServiceDetails.groups: []}
        for groupIdx, group in enumerate(processObj.serviceDetails[ServiceDetails.groups]):
            groupResult = {}
            pressure = -1 # user given
            testType = "" # user given
            if checkIfNestedKeyExists(processObj.processDetails, ProcessDetails.additionalInput, ServiceDetails.groups):
                addInput = processObj.processDetails[ProcessDetails.additionalInput][ServiceDetails.groups][groupIdx]
                if "pressure" in addInput:
                    pressure = addInput["pressure"]
                if "testType" in addInput:
                    testType = addInput["testType"]
            if pressure == -1 or testType == "":
                continue # no simulation preferred or possible
            # if material has all specifications, the simulation can start for each model
            materialOfProcess = group[ServiceDetails.material]
            poissonRatio = -1
            youngsModulus = -1
            yieldingStress = -1
            elongationAtBreak = -1
            for prop in materialOfProcess[MaterialDetails.propList]:
                if prop[NodePropertyDescription.key] == NodePropertiesAMMaterial.poissonRatio:
                    poissonRatio = float(prop[NodePropertyDescription.value])
                elif prop[NodePropertyDescription.key] == NodePropertiesAMMaterial.tensileModulus:
                    youngsModulus = float(prop[NodePropertyDescription.value])
                elif prop[NodePropertyDescription.key] == NodePropertiesAMMaterial.ultimateTensileStrength:
                    yieldingStress = float(prop[NodePropertyDescription.value])
                elif prop[NodePropertyDescription.key] == NodePropertiesAMMaterial.elongationAtBreak:
                    elongationAtBreak = float(prop[NodePropertyDescription.value])
            if poissonRatio != -1 and youngsModulus != -1 and yieldingStress != -1 and elongationAtBreak != -1:
                material = {"Youngs Modulus": youngsModulus, "Poisson Ratio": poissonRatio, "Yielding Stress": yieldingStress, "Elon_at_break": elongationAtBreak}
                for modelID in group[ServiceDetails.models]:
                    stlFile, successfulFetch = getFileReadableStream(session, "", processObj.processID, modelID)
                    if successfulFetch:
                        fileContent = stlFile.read(group[ServiceDetails.models][modelID][FileObjectContent.size])
                        result = run_FEM_test(material, pressure, fileContent, processObj.processID + group[ServiceDetails.models][modelID][FileObjectContent.fileName], testType)
                        if "Error" in result:
                            return Exception(result["Error"])
                        groupResult[modelID] = result
                    else:
                        return Exception("Model could not be fetched")
            else:
                return Exception("Material does not have all specifications")
            resultDict[ServiceDetails.groups].append(groupResult)
        return resultDict
    except Exception as e:
        return e
    