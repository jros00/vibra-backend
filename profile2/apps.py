from django.apps import AppConfig


class Profile2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile2'
    
    def ready(self):
        import profile2.signals
