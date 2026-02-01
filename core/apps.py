from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from core.cloudinary.config import configure_cloudinary
        configure_cloudinary()
        
