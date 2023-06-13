from django.apps import AppConfig


class WebadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webadmin'

    APP_READY=False


    def get_available_groups():

        try:

            if not WebadminConfig.APP_READY:
                return [("","")]

            from .models import ProjectGroup

            groups=[]

            for group in ProjectGroup.objects.all():
                groups.append((group.name,group.project_name))

            return groups

        except:
            return [("","")]
        


    def ready(self) -> None:

        from domena.urls import urlpatterns
        from webadmin.views import reg_form,reg
        from django.urls import path

        urlpatterns.append(path('register/',reg_form))
        urlpatterns.append(path('reg/',reg))

        WebadminConfig.APP_READY=True

        return super().ready()
