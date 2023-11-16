from django.apps import AppConfig
from django.core.checks import register
from .checks import Tags, checkEnv, checkDb, checkRedis
from logging import getLogger
logger = getLogger("django_debug")

#
#
# # for now coping with configuration things, perhaps could be done better with a custom settings class
# # first all settings from base.py and prod|dev|debug.py are loaded database will be set up
# # then belows AppConfig Child's ready function is called and the environment variables are loaded
# # and the real database connection will be set up
# #
from code_General.settings.base import ConfigHelper, BackendConfigHelper


class BackendDjangoConfig(AppConfig, BackendConfigHelper):
    name = 'backend'
    checks_disable = { 'check_env': ('generate_env',), 'check_db' : ('create_db','generate_env'), 'check_redis': ('create_db','generate_env')}

    def __init__(self,app_name, app_module):
        AppConfig.__init__(self,app_name, app_module)
        BackendConfigHelper.__init__(self)

    def ready(self):
        from django.conf import settings
        if self.doCheck('check_env'):
            register(checkEnv, Tags.env_check) # register check_env function with tag env_check
        if self.doCheck('check_db'):
            register(checkDb, Tags.db_check) # register check_db function with tag db_check
        if self.doCheck('check_redis'):
            register(checkRedis, Tags.redis_check)
        super(BackendDjangoConfig, self).ready()

    def __repr__(self):
        return self.name

    def doCheck(self, check_name):
        """
        determine if check should be executed
        :param check_name:
        :type check_name: str
        :return: True if check should be executed
        :rtype: bool
        """

        import sys
        for tokens in sys.argv:
            if tokens in self.checks_disable[check_name]:
                logger.info(f'check {check_name} will be skipped')
                return False
        logger.info(f'check {check_name} will be executed')
        return True
