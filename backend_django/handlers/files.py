import redis, json, os
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=os.environ.get("REDISPW"))

def testRedis(request):
    """
    Save a key:value in redis

    :param request: request
    :type request: HTTP GET
    :return: Response with results of "search"
    :rtype: JSON

    """
    redis_instance.set("testkey", "testvalue")
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
