from django.apps import AppConfig
from domena.plugins import addURL


class LejConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lej'

    APP_READY=False
    
    LAST_UPDATE = 0
    
    def ready(self) -> None:

        from lej.views import ranking_view,check_for_update
        from domena.home import entries
        from domena.menu import entries as menu_entries
        from domena.menu_types import HomeBlock,MenuBlock
        
        addURL('lej/check/',check_for_update)
        addURL('lej/ranking/',ranking_view)
        
        entries.append(HomeBlock("CyberLej","/lej/ranking/"))
        menu_entries.append(MenuBlock("CyberLej","/lej/ranking/"))
    
        self.APP_READY = True

        return super().ready()