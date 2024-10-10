from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """
    Configuration class for the 'user_management' application.

    This class is responsible for configuring the 'user_management' app and ensuring
    that any custom initialization logic (such as signal registration) is executed when
    the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_management'
    
    def ready(self):
        """
        This method is called when the application is ready.

        It is overridden here to import and register any signals for the 'user_management' app.
        By importing the `signals` module, Django ensures that the signal handlers are connected
        to the relevant models.
        """
        from . import signals