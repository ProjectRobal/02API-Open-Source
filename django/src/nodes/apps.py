from django.apps import AppConfig
import logging

class NodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nodes'

    def ready(self) -> None:

        from .models import PublicNode

        logging.debug(PublicNode.__subclasses__())

        return super().ready()
