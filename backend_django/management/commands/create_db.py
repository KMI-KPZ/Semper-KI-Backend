from django.core.management.base import BaseCommand

from django.apps import apps

from backend_django.helper.classes import SemperKiConfigHelper

class Command(BaseCommand):
    help = 'creates database from configured environment variables in apps.py if not exists'

    def handle(self, *args, **options):
        #check if db exists
        from django.conf import settings
        import psycopg2
        connection = None
        try:
            connection = psycopg2.connect(user = settings.DATABASES['default']['USER'],
                                          password = settings.DATABASES['default']['PASSWORD'],
                                          host = settings.DATABASES['default']['HOST'],
                                          port = settings.DATABASES['default']['PORT'],
                                          database = 'postgres')
        except:
            print(f"Error while connecting to PostgreSQL with user {settings.DATABASES['default']['USER']} on host {settings.DATABASES['default']['HOST']} with port {settings.DATABASES['default']['PORT']} and database postgres")
            exit(1)

        connection.autocommit = True
        cur = connection.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        print(f'checking if database "{settings.DATABASES["default"]["NAME"]}" exists')
        rows = cur.fetchall()
        db_exists = False
        for row in rows:
            if row[0] == settings.DATABASES['default']['NAME']:
                db_exists = True
                print(f'Database {settings.DATABASES["default"]["NAME"]} already exists')
                exit(0)
                break
        print(f'Database {settings.DATABASES["default"]["NAME"]} does not exist')
        if not db_exists:
            try:
                cur = connection.cursor()
                cur.execute(f'CREATE DATABASE {settings.DATABASES["default"]["NAME"]};')
                print(f"Database {settings.DATABASES['default']['NAME']} created successfully")
                exit(0)
            except (Exception, psycopg2.DatabaseError) as error:
                #print error
                print(str(error))
                print(f"Error while creating database {settings.DATABASES['default']['NAME']}")
                exit(1)


