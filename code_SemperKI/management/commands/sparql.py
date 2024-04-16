"""
Part of Semper-KI software

Thomas Skodawessely 2023

Contains: ?
"""
import json
import random
from argparse import ArgumentParser

from django.core.management import BaseCommand

from code_General.utilities.sparql import QueryType
from code_SemperKI.services.service_AdditiveManufacturing.connections.cmem import AdditiveQueryManager
from Generic_Backend.code_General.connections.redis import RedisConnection
#from code_SemperKI.services.service_AdditiveManufacturing.connections.cmem import cmemOauthToken, endpoint
import code_SemperKI.connections.cmem as SKICmem
endpoint = SKICmem.endpoint
updateEndpoint = SKICmem.updateEndpoint
cmemOauthToken = SKICmem.oauthToken

####################################################################################
class Command(BaseCommand):
    help = 'list all SemperKI services'

    ####################################################################################

    def add_arguments(self, parser: ArgumentParser):
        # add argument id as integer required
        parser.add_argument('resource', type=str, nargs="?",
                            help='a resource; if not given a list of all resources will be shown')
        parser.add_argument('query_type', type=str, nargs="?",
                            help='query type; if not given but a resource is given all query types of that resource will be shown')
        parser.add_argument('id', type=int, nargs="?",
                            help='an id; if no --insert is given the organisation with that ID will be loaded, if --insert is given a new organisation will be created with that ID')

    def handle(self, *args, **options):
        print(f'Options: \n{options}')
        manager = AdditiveQueryManager(RedisConnection(), cmemOauthToken, endpoint, updateEndpoint)

        # get id from argument
        resource = options['resource']
        queryType = QueryType.__getitem__(options['query_type']) if options['query_type'] is not None else None

        id = options['id']



        if manager.__dict__.get(resource) is None:
            print(f'\nUnknown resource "{resource}"')
            resource = None

        if resource is None:
            self.showResources(manager)
            exit(0)

        if queryType is not None and not manager.__dict__[resource].has(queryType):
            print(f'\nUnknown query type "{queryType}" for resource "{resource}"')
            queryType = None

        if queryType is None:
            print(f'\nQuery types for {resource}:')
            for type in manager.getResourcesAndTypes()[resource]:
                print(f'\t{type}')
            exit(0)

        if id is None and queryType != QueryType.GET:
            print(f'\nNo id given - setting query type to GET')
            queryType = QueryType.GET

        # switch case
        if queryType == QueryType.GET:
            print(json.dumps(manager.__dict__[resource].get({}), indent=4))
        elif queryType == QueryType.INSERT:
            print(manager.__dict__[resource].getVars(QueryType.INSERT))
            print(manager.__dict__[resource].insert({"ID": id, 'name': "Thomas ORGA " + str(id), "Material": "<https://data.semper-ki.org/Material/test-PLA>","PrinterModel" : "Industry F340"}))
        elif queryType == QueryType.UPDATE:
            print(manager.__dict__[resource].update({"ID": id, 'name': "Thomas ORGA " + str(id)}))
        elif queryType == QueryType.DELETE:
            print(manager.__dict__[resource].delete({"ID": id, 'name': "Thomas ORGA " + str(id)}))

        # print(json.dumps(manager.serviceProvider.getAll(), indent=4))
        # print("##############################################")
        # print(manager.serviceProvider.getVars(QueryType.INSERT))
        # print("##############################################")
        # print(manager.serviceProvider.insert({"PrinterModel": "Thomas-Drucker", "ID": id, 'Material': "PLA", 'name': "Thomas ORGA " + str(id)}))
        # print(manager.serviceProvider.getAll())
        exit(0)

    def showResources(self, manager: AdditiveQueryManager):
        resources = manager.getResourcesAndTypes()
        print('List of all resources:')
        for key, value in resources.items():
            print(f'\n{key}: ')
            for type in value:
                print(f'\t{type}')
