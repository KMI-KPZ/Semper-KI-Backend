"""
Part of Semper-KI software

Thomas Skodawessely 2023

Contains: AppConfig

"""

from django.apps import AppConfig

#######################################################
class SemperKIConfig(AppConfig):
    name = "code_SemperKI"
    
    #######################################################
    def __init__(self,app_name, app_module):
        AppConfig.__init__(self,app_name, app_module)
