from django.apps import AppConfig
import threading


class DevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devices'
    websocket:threading.Thread|None=None
    

    def ready(self) -> None:


        return super().ready()
