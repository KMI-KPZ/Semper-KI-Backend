"""
Part of Semper-KI software

Thomas Skodawessely 2023

Contains: Imports for services
"""



from django.apps import AppConfig

####################################################
class CodeSemperKiConfig(AppConfig):
    name = 'code_SemperKI'

    def ready(self):
        import code_SemperKI.imports
