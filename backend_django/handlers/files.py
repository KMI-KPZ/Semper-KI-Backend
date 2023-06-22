"""
Part of Semper-KI software

Silvio Weging 2023

Contains: File upload handling
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
import asyncio, json

from ..handlers.basics import checkIfUserIsLoggedIn

from ..services import crypto, redis, stl, mocks, postgres

#######################################################
def testRedis(request):
    """
    Save a key:value in redis and retrieve it to test if it works.

    :param request: request
    :type request: HTTP GET
    :return: Response with results of "search"
    :rtype: JSON

    """
    redis.addContent("testkey", "testvalue")
    if request.method == "GET":
        result = redis.retrieveContent("testkey")
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

#######################################################
def uploadFileTemporary(request):
    """
    File upload for temporary use, save into redis.

    :param request: request
    :type request: HTTP POST
    :return: Response with success or fail
    :rtype: HTTPResponse

    """
    if request.method == "POST":
        key = request.session.session_key
        fileNames = list(request.FILES.keys())[0]
        files = []
        for name in fileNames:
            files.append( (crypto.generateMD5(name + crypto.generateSalt()), name, request.FILES.getlist(name)[0]) )

        returnVal = redis.addContent(key, files)
        if returnVal is True:
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse(returnVal, status=500)
    
    return HttpResponse("Wrong request method!", status=405)

#######################################################
async def createPreviewForOneFile(inMemoryFile):
    return await stl.stlToBinJpg(inMemoryFile)

async def createPreview(listOfFiles, fileNames):
    return await asyncio.gather(*[createPreviewForOneFile(listOfFiles.getlist(fileName)[0]) for fileName in fileNames])

def uploadModels(request):
    """
    File(s) upload for temporary use, save into redis. File(s) are 3D models

    :param request: request
    :type request: HTTP POST
    :return: Response with mock model of uploaded file
    :rtype: HTTPResponse

    """
    if request.method == "POST":
        try:
            key = request.session.session_key
            fileNames = list(request.FILES.keys())
            files = []
            models = {"models": []}

            previews = asyncio.run(createPreview(request.FILES, fileNames))

            for idx, name in enumerate(fileNames):
                id = crypto.generateMD5(name + crypto.generateSalt())

                model = mocks.getEmptyMockModel()
                model["id"] = id
                model["title"] = name
                model["URI"] = str(previews[idx])
                model["createdBy"] = "user"
                models["models"].append(model)

                # stl.binToJpg(previews[idx])

                files.append( (id, name, previews[idx], request.FILES.getlist(name)[0]) )
            returnVal = redis.addContent(key, files)
            if returnVal is not True:
                return HttpResponse(returnVal, status=500)

            return JsonResponse(models)
        except (Exception) as error:
            print(error)
            return HttpResponse(error, status=500)

    return HttpResponse("Wrong request method!", status=405)

#######################################################
def getUploadedFiles(session_key):
    """
    Retrieve temporary files from redis.

    :param session_key: session_key of user
    :type session_key: string
    :return: Saved content
    :rtype: tuple

    """
    (contentOrError, Flag) = redis.retrieveContent(session_key)
    if Flag is True:
        return contentOrError
    else:
        return None

#######################################################
def testGetUploadedFiles(request):
    return HttpResponse(getUploadedFiles(request.session.session_key), content_type='multipart/form-data')

#######################################################
def downloadFiles(request):
    """
    Send file to user from temporary, later permanent storage

    :param request: Request of user for a specific file of an order
    :type request: HTTP POST
    :return: Saved content
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            content = json.loads(request.body.decode("utf-8"))
            orderID = content["id"]
            fileName = content["filename"]
            currentOrder = postgres.OrderManagement.getOrder(orderID)
            for idx, elem in enumerate(currentOrder.files):
                if fileName == elem["filename"]:
                    (contentOrError, Flag) = redis.retrieveContent(elem["path"])
                    if Flag:
                        return HttpResponse(contentOrError[idx][3], content_type='multipart/form-data')
                        #return FileResponse(contentOrError[idx][3].seek(0)) #, content_type='multipart/form-data')
                    else:
                        return HttpResponse(contentOrError, status=500)
            return HttpResponse("Not found!", status=404)
        else:
            return HttpResponse("Wrong method!", status=405)
    else:
        return HttpResponse("Not logged in", status=401)
    
