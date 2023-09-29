import os
import threading

from django.core.checks import Tags as DjangoTags, Error, Info
from django.core.checks import register
from .helper.classes import SemperKiConfigHelper
from django.db import connections, OperationalError
from django.apps import apps


class Tags(DjangoTags):
    env_check = 'env_check'
    db_check = 'db_check'
    redis_check = 'redis_check'


def checkEnv(app_configs=None, **kwargs):
    print('checking environment variables in thread: '+ str(threading.get_ident()))
    errors = []
    if app_configs is None:
        app_configs = apps.get_app_configs()

    for app in app_configs:
        if issubclass(type(app), SemperKiConfigHelper):
            print(f'checking environment variables for {str(app)}\n')
            errors.extend(app.checkEnvVars())
    return errors


def checkDb(app_configs=None, **kwargs):
    print('checking databases in thread: '+ str(threading.get_ident()))
    errors = []
    if app_configs is None:
        app_configs = apps.get_app_configs()

    for app in app_configs:
        if issubclass(type(app), SemperKiConfigHelper):
            print(f'checking databases for {str(app)}\n')
            for db_alias in app.getDbAliases():
                db_conn = connections[db_alias]
                from django.conf import settings
                db_name = settings.DATABASES[db_alias].get("NAME")
                try:
                    c = db_conn.cursor()
                    errors.append(Info(f'connected to database with alias "{db_alias}" on "{db_conn.settings_dict["HOST"]}"\n db_name: "{db_name}"',id='db_check'))
                except OperationalError:
                    connected = False
                    errors.append(Error(f'could not connect to database with alias "{db_alias}" on "{settings.DATABASES[db_alias]["HOST"]}"\n db_name: "{db_name}"',
                                        hint=f'Check your {os.environ.get("ENV_FILE",".env")} file and it\'s settings and check if database exists',
                                        id='db_check'))
                else:
                    connected = True
    if len(errors) == 0:
        tables = [m._meta.db_table for c in apps.get_app_configs() for m in c.get_models()]
        print(f'all tables by models {str(tables)}\n')

    return errors


def checkRedis(app_configs=None, **kwargs):
    if app_configs is None:
        app_configs = apps.get_app_configs()

    for app in app_configs:
        if issubclass(type(app), SemperKiConfigHelper):
            from .services.redis import addContent, deleteKey, retrieveContent
            try:
                addContent("_test", "test")
                value = retrieveContent("_test")
                deleteKey("_test")
                if value[0] != "test":
                    return [Error(f'could not store and retrieve key', id='redis_check')]
            except Exception as e:
                return [Error(f'could not connect to redis', id='redis_check')]
            return [Info(f'connected to redis and could store, retrieve and delete test-token', id='redis_check')]

    return []