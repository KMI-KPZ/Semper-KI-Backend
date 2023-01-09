from django.test import TestCase
from django.http import HttpRequest, HttpResponse

# Create your tests here.

# import classes here
#from .models import Question

from handlers.test_response import *
class TestTestcalls(TestCase):

    def test_testResponse(self):
        """
        some logic, test if result is as expected
        """
        mockRequest = HttpRequest()
        mockRequest.method = "GET"
        response = testResponse(mockRequest)
        self.assertIs(response["testHeader"] == "TESTHEADER", True)

    def test_testResponseCsrf(self):
        mockRequest = HttpRequest()
        mockRequest.method = "GET"
        response = testResponseCsrf(mockRequest)
        self.assertIs("csrftoken" in response.cookies, True)

# TODO AuthTests