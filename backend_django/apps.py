import os
import signal
import threading

from django.apps import AppConfig

from .services import auth0

from django.core.checks import register
from .checks import Tags, checkEnv, checkDb
from .helper.classes import SemperKiConfigHelper

#
#
# # for now coping with configuration things, perhaps could be done better with a custom settings class
# # first all settings from base.py and prod|dev|debug.py are loaded database will be set up
# # then belows AppConfig Child's ready function is called and the environment variables are loaded
# # and the real database connection will be set up
# #
from backend_django.settings.base import SemperKiConfigHelper, BackendDjangoConfigHelper


class BackendDjangoConfig(AppConfig, BackendDjangoConfigHelper):
    name = 'backend_django'
    checks_disable = { 'check_env': ('generate_env',), 'check_db' : ('create_db','generate_env') }
    def ready(self):
        from django.conf import settings
        print(f'\n\n********** BackendDjangoConfig.ready() **********\nSettings-Module: {settings.BACKEND_SETTINGS}\n')

        if self.doCheck('check_env'):
            register(checkEnv, Tags.env_check) # register check_env function with tag env_check
        if self.doCheck('check_db'):
            register(checkDb, Tags.db_check) # register check_db function with tag db_check
        super(BackendDjangoConfig, self).ready()

    def __repr__(self):
        return self.name

    def doCheck(self, check_name):
        import sys
        for tokens in sys.argv:
            if tokens in self.checks_disable[check_name]:
                print(f'check {check_name} will be skipped')
                return False
        print(f'check {check_name} will be executed')
        return True
