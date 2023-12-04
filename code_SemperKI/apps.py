"""
Part of Semper-KI software

Thomas Skodawessely 2023

Contains: Imports for services
"""

import os
import importlib.util
import sys

from django.apps import AppConfig

####################################################
class CodeSemperKiConfig(AppConfig):
    name = 'code_SemperKI'

    def ready(self):
        currentDirectory = os.getcwd()  # current working directory

        for root, dirs, files in os.walk(currentDirectory):
            if 'imports.py' in files:
                serviceFilePath = os.path.join(root, 'imports.py')

                # create module name by replacing the path separator with dots
                moduleName = os.path.relpath(serviceFilePath, currentDirectory).replace(os.sep, '.').rstrip('.py')

                # import the module
                spec = importlib.util.spec_from_file_location(moduleName, serviceFilePath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[moduleName] = module
                spec.loader.exec_module(module)

                print(f"Imported module {moduleName}")
