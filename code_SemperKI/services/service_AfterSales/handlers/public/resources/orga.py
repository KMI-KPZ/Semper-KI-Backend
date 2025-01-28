"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Calls to ontology for adding and retrieving data
"""

import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization

from code_SemperKI.definitions import *
from code_SemperKI.handlers.private.knowledgeGraphDB import SReqCreateNode, SReqUpdateNode, SResGraphForFrontend, SResNode, SResProperties
from code_SemperKI.services.service_AfterSales.logics.orgaLogic import logicForCloneTestGraphToOrgaForTests
from code_SemperKI.services.service_AfterSales.utilities.basics import checkIfOrgaHasASAsService
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

from ....utilities import sparqlQueries
from ....service import SERVICE_NUMBER

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
