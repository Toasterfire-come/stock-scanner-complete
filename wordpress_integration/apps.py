from django.apps import AppConfig

class WordpressIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wordpress_integration'
    verbose_name = 'WordPress Integration'
    
    def ready(self):
        # Import signals if any
        pass