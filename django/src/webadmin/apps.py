from django.apps import AppConfig
import logging

class WebadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webadmin'

    APP_READY=False

    

    def get_available_groups():

        try:

            if not WebadminConfig.APP_READY:
                logging.warning("Groups are not ready yet!")
                return [("","")]

            from .models import ProjectGroup

            logging.debug("Loading group projects")

            groups=[]

            for group in ProjectGroup.objects.all():
                groups.append((group.name,group.project_name))

            return groups

        except:
            return [("","")]
        


    def ready(self) -> None:

        from domena.urls import urlpatterns
        from webadmin.views import reg_form,reg,profile,update_profile,img_set,generate_new_card,get_id
        from django.urls import path
        from domena.home import entries
        from domena.menu import entries as menu_entries
        from domena.menu_types import HomeBlock,MenuBlock

        urlpatterns.append(path('register/',reg_form))
        urlpatterns.append(path('reg/',reg))
        urlpatterns.append(path('profile/',profile))
        urlpatterns.append(path('userup/',update_profile))
        urlpatterns.append(path('img_set/',img_set))
        urlpatterns.append(path('n_card/',generate_new_card))
        urlpatterns.append(path('uid/',get_id))

        entries.append(HomeBlock("Profile","/profile/"))
        entries.append(HomeBlock("Card register","/register/"))
        menu_entries.append(MenuBlock("Profile","/profile/"))
        menu_entries.append(MenuBlock("Card register","/register/"))

        WebadminConfig.APP_READY=True

        return super().ready()
