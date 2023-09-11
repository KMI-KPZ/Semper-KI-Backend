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
    dbs = ()

    def get_env_vars(self):
        return self.env_vars

    def check_env_vars(self):
        remarks = []
        for env_name in self.env_vars:
            # parameter not given - no default value - required
            if (env_name not in os.environ
                    and self.env_vars[env_name]['required'] is True
                    and self.env_vars[env_name]['default'] is None):
                remarks.append(Error(f'missing environment variable "{env_name}"',
                                     hint=self.env_vars[env_name][
                                              'hint'] + "\n" + ' Check your .env file and sync it with .env.example'
                                     , id='env_check'))
            # parameter not given - default value - required
            elif (env_name not in os.environ and self.env_vars[env_name]['required'] is True
                  and self.env_vars[env_name]['default'] is not None):
                remarks.append(Info(f'omitted environment variable "{env_name}"',
                                       hint=self.env_vars[env_name][
                                                'hint'] + f' chosen default value: "{str(self.env_vars[env_name]["default"])}"' + "\n" + 'Check your .env file and sync it with .env.example',
                                       id='env_check'))
        return remarks

    def load_env_vars(self, target_module):
        for env_name in self.env_vars:
            #print(f'{env_name} : {os.environ.get(env_name, self.env_vars[env_name]["default"])}')
            setattr(target_module,self.env_vars[env_name]['var'],
                                 os.environ.get(env_name, self.env_vars[env_name]['default']))

    def get_db_aliases(self) -> tuple:
        return self.dbs

    def do_check(self) -> bool:
        return True
