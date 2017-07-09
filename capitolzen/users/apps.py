from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'capitolzen.users'
    verbose_name = "Users"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass


class AlertConfig(AppConfig):
    name = 'capitolzen.alerts'
    label = 'alerts'
    verbose_name = 'Alerts'
