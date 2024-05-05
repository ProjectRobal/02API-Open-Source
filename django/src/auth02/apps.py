from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth02'

    def ready(self) -> None:

        from domena.urls import urlpatterns
        from auth02.views import login_form,auth,unauth,perm_fail
        from django.urls import path

        urlpatterns.append(path('login/',login_form))
        urlpatterns.append(path('auth/',auth))
        urlpatterns.append(path('unauth/',unauth))
        urlpatterns.append(path('permf/',perm_fail))

        return super().ready()
