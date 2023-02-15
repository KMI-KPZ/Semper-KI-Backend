import redis, json, os, pickle
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=os.environ.get("REDISPW"))

#######################################################
def testRedis(request):
    """
    Save a key:value in redis and retrieve it to test if it works

    :param request: request
    :type request: HTTP GET
    :return: Response with results of "search"
    :rtype: JSON

    """
    redis_instance.set("testkey", "testvalue")
    redis_instance.expire("testkey", 10)
    if request.method == "GET":
        items = {}
        count = 0
        for key in redis_instance.keys("*"):
            items[key.decode("utf-8")] = (redis_instance.get(key)).decode("utf-8")
            count += 1
        response = {
            'count': count,
            'msg': f"Found {count} items.",
            'items': items
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

# TODO: DB: hash filepath from user id, create folder, connect user id and filepath and save into postgres
# TODO: Upload: get file, save into redis with session id as key
# TODO: Save file: get file from frontend, encode with user id, get filepath from postgres and save file

#######################################################
def uploadFileTemporary(request):
    # TODO: delete key:file pair after submit
    """
    File upload for temporary use, save into redis

    :param request: request
    :type request: HTTP POST
    :return: Response with success or fail
    :rtype: HTTPResponse

    """
    if request.method == "POST":
        key = request.session.session_key
        files = request.FILES.getlist('File')
        try:
            redis_instance.set(key, pickle.dumps(files))
            redis_instance.expire(key, 86400) # 24 hours until deletion of the file
            return HttpResponse("Success", status=200)
        except (Exception) as error:
            print(error)
            return HttpResponse(error, status=500)
    
    return HttpResponse("Wrong request method!", status=405)

#######################################################
def getUploadedFiles(session_key):
    """
    Retrieve temporary files from redis

    :param session_key: session_key of user
    :type request: string
    :return: Files
    :rtype: binary

    """
    files = pickle.loads(redis_instance.get(session_key))
    redis_instance.delete(session_key)
    return files

#######################################################
def testGetUploadedFiles(request):
    return HttpResponse(getUploadedFiles(request.session.session_key), content_type='multipart/form-data')


    
