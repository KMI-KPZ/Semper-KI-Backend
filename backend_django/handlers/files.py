"""
Part of Semper-KI software

Silvio Weging 2023

Contains: File upload handling
"""

import asyncio, json, logging, zipfile

from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse

from io import BytesIO
from django.views.decorators.http import require_http_methods

from django.utils import timezone

from ..utilities import crypto, mocks, stl

from ..services.postgresDB import pgProfiles, pgProcesses

from ..utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, Logging, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from ..handlers.projectAndProcessManagement import updateProcessFunction, getProcessAndProjectFromSession

from ..services import redis, aws

logger = logging.getLogger("logToFile")

#######################################################
@require_http_methods(["POST"])
def uploadModel(request):
    """
    File upload for 3D model

    :param request: request
    :type request: HTTP POST
    :return: Response with information about the file
    :rtype: JSONResponse

    """
    try:
        info = request.POST 
        projectID = info["projectID"]
        processID = info["processID"]
        fileTags = info["tags"].split(",")
        fileLicenses = info["license"].split(",")
        fileCertificates = info["certificate"].split(",")

        fileName = list(request.FILES.keys())[0]
        fileID = crypto.generateURLFriendlyRandomString()
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        model = {fileName: {}}
        model[fileName]["id"] = fileID
        model[fileName]["title"] = fileName
        model[fileName]["tags"] = fileTags
        model[fileName]["date"] = str(timezone.now())
        model[fileName]["licenses"] = fileLicenses
        model[fileName]["certificates"] = fileCertificates
        model[fileName]["URI"] = ""
        model[fileName]["createdBy"] = userName

        returnVal = aws.manageLocalAWS.uploadFile(processID+"/"+fileID, request.FILES.getlist(fileName)[0])
        if returnVal is not True:
            return JsonResponse({}, status=500)
        
        # Save into files field of the process 
        changes = {"changes": {"files": model, "service": {"model": model[fileName]}}}
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return JsonResponse({}, status=401)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},model {fileName},"+str(datetime.now()))
        return JsonResponse(model)
    except (Exception) as error:
        print(error)
        return JsonResponse({}, status=500)

#######################################################
@require_http_methods(["POST"])
def uploadFiles(request):
    """
    Generic file upload for a process

    :param request: Request with files in it
    :type request: HTTP POST
    :return: Successful or not
    :rtype: HTTP Response
    """
    try:
        info = request.POST
        projectID = info["projectID"]
        processID = info["processID"]
        fileNames = list(request.FILES.keys())
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)

        changes = {"changes": {"files": {}}}
        for fileName in fileNames:
            changes["changes"]["files"][fileName] = {}
            fileID = crypto.generateURLFriendlyRandomString()
            changes["changes"]["files"][fileName]["id"] = fileID
            changes["changes"]["files"][fileName]["title"] = fileName
            changes["changes"]["files"][fileName]["date"] = str(timezone.now())
            changes["changes"]["files"][fileName]["createdBy"] = userName

            returnVal = aws.manageLocalAWS.uploadFile(processID+"/"+fileID, request.FILES.getlist(fileName)[0])
            if returnVal is not True:
                return JsonResponse({}, status=500)
            #returnVal = aws.manageRemoteAWS.uploadFile(processID+"/"+fileID, request.FILES.getlist(fileName)[0])
        
        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return JsonResponse({}, status=401)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},files,"+str(datetime.now()))
        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed", status=500)
    
#######################################################
@require_http_methods(["GET"])
def downloadFile(request, processID, fileID):
    """
    Send file to user from storage

    :param request: Request of user for a specific file of a process
    :type request: HTTP POST
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Saved content
    :rtype: FileResponse

    """
    try:
        # Retrieve the files infos from either the session or the database
        filesOfThisProcess = {}
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            filesOfThisProcess = currentProcess["files"]
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
                currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                filesOfThisProcess = currentProcess.files
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        # retrieve the correct file and download it from aws to the user
        for elem in filesOfThisProcess:
            if "id" in filesOfThisProcess[elem] and filesOfThisProcess[elem]["id"] == fileID:
                content, Flag = aws.manageLocalAWS.downloadFile(processID+"/"+fileID)
                if Flag is False:
                    content, Flag = aws.manageRemoteAWS.downloadFile(processID+"/"+fileID)
                    if Flag is False:
                        return HttpResponse("Not found!", status=404)
                    
                logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},file {filesOfThisProcess[elem]['title']}," + str(datetime.now()))
                    
                return FileResponse(content, filename=filesOfThisProcess[elem]["title"], as_attachment=True) #, content_type='multipart/form-data')
        
        return HttpResponse("Not found!", status=404)
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed", status=500)

#######################################################
@require_http_methods(["GET"])
def downloadFilesAsZip(request, processID):
    """
    Send files to user as zip

    :param request: Request of user for all selected files of a process
    :type request: HTTP POST
    :param processID: process ID
    :type processID: Str
    :return: Saved content
    :rtype: FileResponse

    """
    try:
        fileIDs = request.GET['fileIDs'].split(",")
        filesArray = []

        # Retrieve the files infos from either the session or the database
        filesOfThisProcess = {}
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            filesOfThisProcess = currentProcess["files"]
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
                currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                filesOfThisProcess = currentProcess.files
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        # get files, download them from aws, put them in an array together with their name
        for elem in filesOfThisProcess:
            currentEntry = filesOfThisProcess[elem]
            if "id" in currentEntry and currentEntry["id"] in fileIDs:
                content, Flag = aws.manageLocalAWS.downloadFile(processID+"/"+currentEntry["id"])
                if Flag is False:
                    content, Flag = aws.manageRemoteAWS.downloadFile(processID+"/"+currentEntry["id"])
                    if Flag is False:
                        return HttpResponse("Not found!", status=404)
                
                filesArray.append( (currentEntry["title"], content) )

        if len(filesArray) == 0:
            return HttpResponse("Not found!", status=404)
        
        # compress each file and put them in the same zip file, all in memory
        zipFile = BytesIO()
        with zipfile.ZipFile(zipFile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in filesArray:
                zf.writestr(f[0], f[1].read())
        zipFile.seek(0) # reset zip file

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},files as zip," + str(datetime.now()))        
        return FileResponse(zipFile, filename=processID+".zip", as_attachment=True) #, content_type='multipart/form-data')

    except (Exception) as error:
        print(error)
        return HttpResponse("Failed", status=500)


#######################################################
@require_http_methods(["DELETE"])
def deleteFile(request, processID, fileID):
    """
    Delete a file from storage

    :param request: Request of user for a specific file of a process
    :type request: HTTP DELETE
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Successful or not
    :rtype: HTTPResponse

    """
    try:

        # Retrieve the files infos from either the session or the database
        modelOfThisProcess = {}
        filesOfThisProcess = {}
        liesInDatabase = False
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            if "model" in currentProcess["service"]:
                modelOfThisProcess = currentProcess["service"]["model"]
            filesOfThisProcess = currentProcess["files"]
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteFile.__name__):
                currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                if "model" in currentProcess.service:
                    modelOfThisProcess = currentProcess.service["model"]
                filesOfThisProcess = currentProcess.files
                liesInDatabase = True
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)
        
        deletions = {"changes": {}, "deletions": {}}
        for entry in filesOfThisProcess:
            if fileID == filesOfThisProcess[entry]["id"]:
                deletions["deletions"]["files"] = {filesOfThisProcess[entry]["title"]: {}}
                break
        if modelOfThisProcess != {} and fileID == modelOfThisProcess["id"]:
            deletions["deletions"]["service"] = {"model": {}}
        
        message, flag = updateProcessFunction(request, deletions, currentProjectID, [processID])
        if flag is False:
            return HttpResponse("Not logged in", status=401)
        if isinstance(message, Exception):
            raise message
        
        if not liesInDatabase: # file deletion in database already triggers file deletion in aws
            returnVal = aws.manageLocalAWS.deleteFile(processID+"/"+fileID)
            if returnVal is not True:
                raise Exception("Deletion of file" + fileID + " failed")

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},file {fileID}," + str(datetime.now()))        
        return HttpResponse("Success", status=200)
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed", status=500)

############################################################################################
#######################################################
@require_http_methods(["GET"])
def testRedis(request):
    """
    Save a key:value in redis and retrieve it to test if it works.

    :param request: request
    :type request: HTTP GET
    :return: Response with results of "search"
    :rtype: JSON

    """
    redis.RedisConnection().addContent("testkey", "testvalue")
    if request.method == "GET":
        result = redis.RedisConnection().retrieveContent("testkey")
        response = {
            'result': result,
        }
        return JsonResponse(response, status=200)
    # elif request.method == "POST":
    #     item = json.loads(request.body)
    #     key = list(item.keys())[0]
    #     value = item[key]
    #     redis_instance.set(key, value)
    #     response = {
    #         'msg': f"{key} successfully set to {value}"
    #     }
    #     return JsonResponse(response, 201)

# #######################################################
# @require_http_methods(["POST"])
# def uploadFileTemporary(request):
#     """
#     File upload for temporary use, save into redis.

#     :param request: request
#     :type request: HTTP POST
#     :return: Response with success or fail
#     :rtype: HTTPResponse

#     """
#     if request.method == "POST":
#         key = request.session.session_key
#         fileNames = list(request.FILES.keys())[0]
#         files = []
#         for name in fileNames:
#             files.append( (crypto.generateMD5(name + crypto.generateSalt()), name, request.FILES.getlist(name)[0]) )

#         returnVal = redis.RedisConnection().addContent(key, files)
#         if returnVal is True:
#             return HttpResponse("Success", status=200)
#         else:
#             return HttpResponse(returnVal, status=500)
    
#     return HttpResponse("Wrong request method!", status=405)

#######################################################
# async def createPreviewForOneFile(inMemoryFile):
#     return await stl.stlToBinJpg(inMemoryFile)

# async def createPreview(listOfFiles, fileNames):
#     return await asyncio.gather(*[createPreviewForOneFile(listOfFiles.getlist(fileName)[0]) for fileName in fileNames])


# #######################################################
# def getUploadedFiles(session_key):
#     """
#     Retrieve temporary files from redis.

#     :param session_key: session_key of user
#     :type session_key: string
#     :return: Saved content
#     :rtype: tuple

#     """
#     #(contentOrError, Flag) = redis.RedisConnection().retrieveContent(session_key)
#     contentOrError, Flag = aws.manageLocalAWS.downloadFile(session_key)
#     if Flag is True:
#         return contentOrError
#     else:
#         return None

# #######################################################
# def testGetUploadedFiles(request):
#     return HttpResponse(getUploadedFiles(request.session.session_key), content_type='multipart/form-data')
