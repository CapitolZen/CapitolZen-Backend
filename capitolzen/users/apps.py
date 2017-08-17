from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'capitolzen.users'
    verbose_name = "Users"

    def ready(self):
        import capitolzen.users.signals  # noqa
