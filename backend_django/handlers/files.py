from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import asyncio

from ..services import crypto, redis, stl, mocks

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
            models["models"].append(model)

            # stl.binToJpg(previews[idx])

            files.append( (id, name, previews[idx], request.FILES.getlist(name)[0]) )

        returnVal = redis.addContent(key, files)
        if returnVal is not True:
            return HttpResponse(returnVal, status=500)

        return JsonResponse(models)

    
    return HttpResponse("Wrong request method!", status=405)

#######################################################
def getUploadedFiles(session_key):
    """
    Retrieve temporary files from redis.

    :param session_key: session_key of user
    :type request: string
    :return: Files
    :rtype: binary

    """
    (contentOrError, Flag) = redis.retrieveContent(session_key)
    if Flag is True:
        return contentOrError
    else:
        return None

#######################################################
def testGetUploadedFiles(request):
    return HttpResponse(getUploadedFiles(request.session.session_key), content_type='multipart/form-data')


    
