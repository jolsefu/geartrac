from django.apps import AppConfig



class GeartracAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'geartrac_app'

    def ready(self):
        import geartrac_app.signals
