from django.core.management import BaseCommand
from ...services import serviceManager

class Command(BaseCommand):
    help = 'list all SemperKI services'

    def handle(self, *args, **options):
        services = serviceManager.getAllServices()
        print("Available services:")
        for elem in services:
            print(f"{elem}: {services[elem]['name']}")
        exit(0)
