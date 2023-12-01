from django.apps import AppConfig


class CodeSemperKiConfig(AppConfig):
    name = 'code_SemperKI'

    def ready(self):
        import code_SemperKI.imports
