from django.apps import AppConfig

SERVICE_IMPORT_PATH="services.imported"

SERVICE_UPLOAD_PATH="/app/services/imported"


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
