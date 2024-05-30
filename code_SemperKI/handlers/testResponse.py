"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""
import platform, subprocess, json, requests

from django.http import HttpResponse, JsonResponse

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

from code_SemperKI.utilities.basics import ExceptionSerializer

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
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from drf_spectacular.utils import extend_schema
from rest_framework.views import exception_handler
import io

# @api_view(['GET'])
# def restTest(request, dummy:str):
#     if request.method == "GET":
#         return Response("Test "+dummy, status=status.HTTP_200_OK)
    
class restTestAPI(APIView):

    class RequestSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)
        
    class ResponseSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)
        dummy = serializers.CharField(max_length=100)

    @extend_schema(
        operation_id="test",
        summary="Test",
        description="Test",
        responses={
            200: ResponseSerializer
        },
    )
    def get(self, request, dummy:str, format=None):
        return Response({"name": "test", "age": 12, "dummy": dummy}, status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="test2",
        summary="Test2",
        description="Test2",
        request=RequestSerializer,
        responses={
            200: ResponseSerializer,
            400: ExceptionSerializer
        },
    )
    def post(self, request, dummy:str, format=None):
        json_data=request.body
        stream= io.BytesIO(json_data)
        jsonContent = JSONParser().parse(stream)
        serializer = self.RequestSerializer(data=jsonContent)
        if serializer.is_valid():
            validatedInput = serializer.data
            validatedInput["dummy"]=dummy
            outSerializer = self.ResponseSerializer(validatedInput)
            output = JSONRenderer().render(outSerializer.data)
            return Response(output, status=status.HTTP_200_OK)
        else:
            exceptionSerializer = self.ExceptionSerializer(serializer.errors)
            return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)

    