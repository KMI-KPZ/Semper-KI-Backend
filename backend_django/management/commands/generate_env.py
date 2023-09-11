from django.core.management.base import BaseCommand

from django.apps import apps

from backend_django.helper.classes import SemperKiConfigHelper

class Command(BaseCommand):
    help = 'generates .env.example file from configured environment variables in apps.py'
    file_intro = ('# This is an example .env file for Semper-KI with following structure:\n'
                  '# ENV_VARNAME=[DEFAULT_VALUE|Nothing] # required? - comment')
    current_values = ('# Current values are:\n')

    def add_arguments(self, parser):
        parser.add_argument('-p','--print',action="store_true", help='Should current parameters be printed?')
    def handle(self, *args, **options):
        from django.conf import settings
        import os
        print('Current options:')
        print(str(options))
        s= "POSTGRES_HOST"
        print(f'\n\n{s} -> os says {os.environ.get(s)} and settings says {settings.__getattr__(s)}\n\n')
        semper_ki_cfgs = [app_cfg for app_cfg in apps.get_app_configs() if issubclass(type(app_cfg), SemperKiConfigHelper)]
        self.stdout.write (self.file_intro if not options['print'] else self.current_values)
        for app in semper_ki_cfgs:
            self.stdout.write(f'\n#AppConfig "{str(app)}"')
            env_vars = app.get_env_vars().items()
            #print keys
            for key, value in env_vars:
                val = os.environ.get(key,'') if options.get('print') else ( value["default"] if value["default"] else "" )
                self.stdout.write('{: <100}'.format(f'{key}={val}') + f'# {"required - " if value["required"] else ""}{value["hint"]}')

