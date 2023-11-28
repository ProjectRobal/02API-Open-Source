from django.apps import AppConfig
from domena.signals import onLogin,onLogout
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
    
    @staticmethod
    def on_user_login(sender,user,request,**kwargs):
        
        from webadmin.models import CardNode

        try:

            CardNode.objects.get(user=user)

        except CardNode.DoesNotExist:

            logging.info("No card for specified user: "+str(user.username)+" generating new card!")
            card:CardNode=CardNode(user=user)

            card.save()



    def ready(self) -> None:

        from domena.urls import urlpatterns
        from webadmin.views import reg_form,reg,profile,update_profile,img_set,generate_new_card,get_id,cards_view,logout_from_basement
        from django.urls import path
        from domena.home import entries
        from domena.menu import entries as menu_entries
        from domena.menu_types import HomeBlock,MenuBlock

        urlpatterns.append(path('webadmin/profile/',profile))
        urlpatterns.append(path('webadmin/img_set/',img_set))
        urlpatterns.append(path('webadmin/n_card/',generate_new_card))
        urlpatterns.append(path('webadmin/l_base/',logout_from_basement))
        urlpatterns.append(path('webadmin/uid/',get_id))
        urlpatterns.append(path('webadmin/lscards/',cards_view))

        entries.append(HomeBlock("Profile","/webadmin/profile/"))
        entries.append(HomeBlock("Basement status","/webadmin/lscards/"))
        menu_entries.append(MenuBlock("Profile","/webadmin/profile/"))
        menu_entries.append(MenuBlock("Basement status","/webadmin/lscards/"))

        onLogin(WebadminConfig.on_user_login)

        WebadminConfig.APP_READY=True

        return super().ready()
