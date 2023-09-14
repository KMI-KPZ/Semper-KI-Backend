from asgiref.local import Local
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.apps import AppConfig
from django.core.checks import Warning, Error, Info
from django.conf import LazySettings
# from django.db import ConnectionHandler
import os

# def setup_dbs_in_connection_handler(db_configs, connection_handler_original: ConnectionHandler):
#     import threading
#     print('setting up databases in connection handler for thread ' + str(threading.current_thread().ident))
#     connection_handler = ConnectionHandler(db_configs)
#     for alias in db_configs:
#         print(f'creating connection for {alias}')
#         sync_to_async(connection_handler.__setitem__(alias,connection_handler.create_connection(alias)), thread_sensitive=True)
#
#     connection_handler_original._connections = connection_handler._connections


class SemperKiConfigHelper:
    env_vars = {}
    env_vars_internal = {}
    env_vars_external = {}

    dbs = ()

    def getEnvVars(self):
        return self.env_vars

    def getEnvVarsInternal(self):
        return self.env_vars_internal

    def getEnvVarsExternal(self):
        return self.env_vars_external

    def checkEnvVars(self):
        remarks = []
        for env_name in self.getEnvVars():
            # parameter not given - no default value - required
            if (env_name not in os.environ
                    and self.env_vars[env_name]['required'] is True
                    and self.env_vars[env_name]['default'] is None):
                remarks.append(Error(f'missing environment variable "{env_name}"',
                                     hint=self.env_vars[env_name][
                                              'hint'] + "\n" + f' Check your {os.environ.get("ENV_FILE",".env")} file '
                                     , id='env_check'))
            # parameter not given - default value - required
            elif (env_name not in os.environ and self.env_vars[env_name]['required'] is True
                  and self.env_vars[env_name]['default'] is not None):
                remarks.append(Info(f'omitted environment variable "{env_name}"',
                                       hint=self.env_vars[env_name][
                                                'hint'] + f' chosen default value: "{str(self.env_vars[env_name]["default"])}"' + "\n" + f'Check your {os.environ.get("ENV_FILE",".env")} file ',
                                       id='env_check'))
        return remarks

    def loadEnvVars(self, target_module):
        for env_name in self.getEnvVars():
            #print(f'{env_name} : {os.environ.get(env_name, self.env_vars[env_name]["default"])}')
            setattr(target_module,self.env_vars[env_name]['var'],
                                 os.environ.get(env_name, self.env_vars[env_name]['default']))

    def getDbAliases(self) -> tuple:
        return self.dbs

    def doCheck(self) -> bool:
        return True
