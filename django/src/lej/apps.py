from django.apps import AppConfig


class LejConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lej'

    APP_READY=False
    
    def ready(self) -> None:

        from webadmin.views import profile,update_profile,img_set,generate_new_card,get_id,cards_view,logout_from_basement,program_card,clear_program_card,logout_user_from_basement
        from domena.home import entries
        from domena.menu import entries as menu_entries
        from domena.menu_types import HomeBlock,MenuBlock

        pass

        return super().ready()