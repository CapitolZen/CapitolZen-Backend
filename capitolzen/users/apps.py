from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'capitolzen.users'
    verbose_name = "Users"

    def ready(self):
        import capitolzen.users.signals  # noqa


class AlertConfig(AppConfig):
    name = 'capitolzen.alerts'
    label = 'alerts'
    verbose_name = 'Alerts'
