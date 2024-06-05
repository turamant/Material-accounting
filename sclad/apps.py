from django.apps import AppConfig

class SkladConfig(AppConfig):
    name = 'sclad'

    def ready(self):
        from . import templatetags