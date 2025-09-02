from django.apps import AppConfig

class NetworksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "networks"

    def ready(self):
        from . import signals  # noqa
        # Ensures the signals are imported and registered