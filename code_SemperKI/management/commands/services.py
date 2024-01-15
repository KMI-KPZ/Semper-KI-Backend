"""
Part of Semper-KI software

Thomas Skodawessely 2023

Contains: ?
"""

from django.core.management import BaseCommand
from ...serviceManager import serviceManager

####################################################################################
class Command(BaseCommand):
    help = 'list all SemperKI services'

    def handle(self, *args, **options):
        services = serviceManager.getAllServices()
        print("Available services:")
        for elem in services:
            print(f"{elem}: {services[elem]['name']}")
        exit(0)
