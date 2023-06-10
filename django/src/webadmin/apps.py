from django.apps import AppConfig


class WebadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webadmin'

    APP_READY=False


    def get_available_groups():

        if not WebadminConfig.APP_READY:
            return []

        from .models import ProjectGroup

        groups=[]

        for group in ProjectGroup.objects.all():
            groups.append((group.name,group.project_name))


        return groups


    def ready(self) -> None:

        WebadminConfig.get_available_groups()

        WebadminConfig.APP_READY=True

        return super().ready()
