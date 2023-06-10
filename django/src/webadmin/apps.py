from django.apps import AppConfig


class WebadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webadmin'

    AVAILABLE_GROUPS=[]

    def get_available_groups():

        from .models import ProjectGroup

        groups=[]

        for group in ProjectGroup.objects.all():
            groups.append((group.name,group.project_name))

        WebadminConfig.AVAILABLE_GROUPS=groups

        return groups


    def ready(self) -> None:

        WebadminConfig.get_available_groups()

        return super().ready()
