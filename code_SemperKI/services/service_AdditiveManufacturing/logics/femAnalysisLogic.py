"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic for FEM analysis
"""
import logging
from multiprocessing import Process as MPProcess, Queue as MPQueue

from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from code_SemperKI.logics.filesLogics import getFileReadableStream
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process
from code_SemperKI.definitions import ProcessDetails

from ..tasks.femSimulationTask import run_FEM_test
from ..definitions import *

loggerError = logging.getLogger("errors")
##################################################
def startFEMAnalysis(session, processObj:Process) -> dict|Exception: 
    """
    Start the FEM Analysis on eligable models and materials
    
    """
    try:
        resultDict = {ServiceDetails.groups: []}
        for groupIdx, group in enumerate(processObj.serviceDetails[ServiceDetails.groups]):
            groupResult = {"groupID": groupIdx, "models": []}
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
            material = {"Youngs Modulus": youngsModulus, "Poisson Ratio": poissonRatio, "Yielding Stress": yieldingStress, "Elon_at_break": elongationAtBreak}
            for modelID in group[ServiceDetails.models]:
                modelResult = {}
                if FileContentsAM.femRequested not in group[ServiceDetails.models][modelID] or not group[ServiceDetails.models][modelID][FileContentsAM.femRequested]:
                    continue
                if poissonRatio == -1 or youngsModulus == -1 or yieldingStress == -1 or elongationAtBreak == -1:
                    modelResult = {"name": group[ServiceDetails.models][modelID][FileObjectContent.fileName], "type": "MATERIAL"}
                else:
                    if FileContentsAM.testType in group[ServiceDetails.models][modelID]:
                        testType = group[ServiceDetails.models][modelID][FileContentsAM.testType]
                    else:
                        testType = "elongation"
                    if FileContentsAM.pressure in group[ServiceDetails.models][modelID]:
                        pressure = group[ServiceDetails.models][modelID][FileContentsAM.pressure] * 1000000 # convert to Pa
                    else:
                        pressure = 0
                    fromRepo = False
                    if FileObjectContent.deleteFromStorage in group[ServiceDetails.models][modelID]:
                        if group[ServiceDetails.models][modelID][FileObjectContent.deleteFromStorage] is False:
                            fromRepo = True
                    stlFile, successfulFetch = getFileReadableStream(session, "", processObj.processID, modelID, fromRepo)
                    if successfulFetch:
                        fileContent = stlFile.read(group[ServiceDetails.models][modelID][FileObjectContent.size])
                        resultQueue = MPQueue()
                        femProcess = MPProcess(target=run_FEM_test, args=(material, pressure, fileContent, processObj.processID + group[ServiceDetails.models][modelID][FileObjectContent.fileName], testType, resultQueue))
                        femProcess.start()
                        femProcess.join(7200)
                        exitCode = femProcess.exitcode
                        result = {}
                        if not resultQueue.empty():
                            result = resultQueue.get()
                        femProcess.close()
                        #result = run_FEM_test(material, pressure, fileContent, processObj.processID + group[ServiceDetails.models][modelID][FileObjectContent.fileName], testType, result)
                        if exitCode != 0:
                            modelResult = {"name": group[ServiceDetails.models][modelID][FileObjectContent.fileName], "type": "ERROR", "ssi": "Process terminated with exit code " + str(exitCode)}
                        else:
                            if "Error" in result:
                                modelResult = {"name": group[ServiceDetails.models][modelID][FileObjectContent.fileName], "type": "ERROR", "ssi": result["Error"]}
                            if "Plastische Verschiebung?" in result and result["Plastische Verschiebung?"]:
                                modelResult = {"name": group[ServiceDetails.models][modelID][FileObjectContent.fileName], "type": "BREAKS"}
                    else:
                        modelResult = {"name": group[ServiceDetails.models][modelID][FileObjectContent.fileName], "type": "MODEL"}
                if modelResult != {}:
                    groupResult["models"].append(modelResult)
            if groupResult["models"] != []:
                resultDict[ServiceDetails.groups].append(groupResult)
        return resultDict
    except Exception as e:
        loggerError.error("Error in startFEMAnalysis: " + str(e))
        return resultDict
    