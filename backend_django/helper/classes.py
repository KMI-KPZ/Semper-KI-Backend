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

    def __init__(self):
        self.env_vars = dict(self.env_vars_internal, **self.env_vars_external)

    def getEnvVars(self):
        return self.env_vars

    def getEnvVarsInternal(self):
        return self.env_vars_internal

    def getEnvVarsExternal(self):
        return self.env_vars_external

    def checkEnvVars(self):
        remarks = []
        for env_name, env_value in self.getEnvVars().items():
            # parameter not given - no default value - required
            if (env_name not in os.environ
                    and env_value['required'] is True
                    and env_value['default'] is None):
                remarks.append(Error(f'missing environment variable "{env_name}"',
                                     hint=env_value[
                                              'hint'] + "\n" + f' Check your {os.environ.get("ENV_FILE",".env")} file '
                                     , id='env_check'))
            # parameter not given - default value - required
            elif (env_name not in os.environ and env_value['required'] is True
                  and env_value['default'] is not None):
                remarks.append(Info(f'omitted environment variable "{env_name}"',
                                       hint= env_value[
                                                'hint'] + f' chosen default value: "{str(env_value["default"])}"' + "\n" + f'Check your {os.environ.get("ENV_FILE",".env")} file ',
                                       id='env_check'))
        return remarks

    def loadEnvVars(self, target_module):
        for env_name in self.env_vars:
            #print(f'{env_name} : {os.environ.get(env_name, self.env_vars[env_name]["default"])}')
            if self.env_vars[env_name].get('type',None) == 'list':
                print(f'****************{env_name} : {os.environ.get(env_name, self.env_vars[env_name]["default"]).split(",")} ***********************')
                setattr(target_module,self.env_vars[env_name]['var'],
                        os.environ.get(env_name, self.env_vars[env_name]['default']).split(','))
                print(f'****************{env_name} : {getattr(target_module,self.env_vars[env_name]["var"])} ***********************')
            else:
                setattr(target_module,self.env_vars[env_name]['var'],
                                 os.environ.get(env_name, self.env_vars[env_name]['default']))

    def getDbAliases(self) -> tuple:
        return self.dbs

    def doCheck(self) -> bool:
        return True


class LazyConnect(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for key, value in attrs.items():
            if callable(value):
                # Wenn das Attribut eine Methode ist, wickle sie in einen Wrapper ein
                new_attrs[key] = cls.wrap_method(value)
            else:
                new_attrs[key] = value

        new_attrs["lazy_fn"] = None
        new_attrs["lazy_fn_called"] = False
        new_attrs['setLazyFn'] = cls.setLazyFn
        return super().__new__(cls, name, bases, new_attrs)

    @classmethod
    def wrap_method(cls,method):
        def wrapper(instance,*args, **kwargs):
            # Hier wird deine zusätzliche Aufgabe ausgeführt
            if method.__name__ not in ("setLazyFn", "__init__") and not instance.lazy_fn_called:
                print(f"Initialisierung von {method.__name__}")
                instance.lazy_fn(instance)
                instance.lazy_fn_called = True

            result = method(instance, *args, **kwargs)
            # Hier wird die Originalmethode aufgerufen
            print(f"Nach Ausführung von {method.__name__}")
            return result
        return wrapper

    def setLazyFn(instance, func):
        instance.lazy_fn = func