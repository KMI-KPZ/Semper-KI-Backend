"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""
import platform, subprocess, json, requests

from django.http import HttpResponse, JsonResponse

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

###################################################
@require_http_methods(["POST", "GET"])
def isMagazineUp(request):
    """
    Pings the magazine website and check if that works or not

    :param request: GET/POST request
    :type request: HTTP GET/POST
    :return: Response with True or False 
    :rtype: JSON Response

    """
    if request.method == "POST":
        try:
            content = json.loads(request.body.decode("utf-8"))
            response = {"up": True}
            for entry in content["urls"]:
                resp = requests.get(entry)
                if resp.status_code != 200:
                    response["up"] = False
                
            return JsonResponse(response)
        except Exception as e:
            return HttpResponse(e, status=500)
    elif request.method == "GET":
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '2', 'magazin.semper-ki.org', '-4']

        response = {"up": True}
        pRet = subprocess.run(command)
        if pRet.returncode != 0:
            response["up"] = False
        return JsonResponse(response)



###################################################
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

@api_view(['GET'])
def restTest(request, dummy:str):
    if request.method == "GET":
        return Response("Test "+dummy, status=status.HTTP_200_OK)
    
class restTestAPI(APIView):

    class RequestSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)

        def create(self, validated_data):
            return {**validated_data}

        def update(self, instance, validated_data):
            instance.name = validated_data.get('name', instance.name)
            instance.age = validated_data.get('age', instance.age)
            return instance
        
    class ResponseSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)

    @extend_schema(
        operation_id="test",
        summary="Test",
        description="Test",
        request=requestSerializer,
        responses={
            200: responseSerializer,
        },
    )
    def get(self, request, dummy:str, format=None):
        return Response({"name": "test", "age": 12}, status=status.HTTP_200_OK)
    
    def post(self, request, dummy:str, format=None):
        serializer = self.RequestSerializer(request.body.decode("utf-8"))
        return Response({"name": "post", "age": 12}, status=status.HTTP_200_OK)
