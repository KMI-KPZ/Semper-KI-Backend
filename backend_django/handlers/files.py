from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from ..services import redis

# TODO: DB: hash filepath from user id, create folder, connect user id and filepath and save into postgres
# TODO: Upload: get file, save into redis with session id as key
# TODO: Save file: get file from frontend, encode with user id, get filepath from postgres and save file

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
        fileName = list(request.FILES.keys())[0]
        files = request.FILES.getlist(fileName)[0]
        returnVal = redis.addContent(key, (fileName, files))
        if returnVal is True:
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse(returnVal, status=500)
    
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


    
