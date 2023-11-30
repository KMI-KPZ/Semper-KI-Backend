"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Modules that need to be imported

"""
import os
import importlib.util
import sys

current_directory = os.getcwd()  # current working directory

for root, dirs, files in os.walk(current_directory):
    if 'service.py' in files:
        service_file_path = os.path.join(root, 'service.py')

        # create module name by replacing the path separator with dots
        module_name = os.path.relpath(service_file_path, current_directory).replace(os.sep, '.').rstrip('.py')

        # import the module
        spec = importlib.util.spec_from_file_location(module_name, service_file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        print(f"Imported module {module_name}")

