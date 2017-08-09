from __future__ import unicode_literals

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    name = 'capitolzen.organizations'
    label = 'organizations'
    verbose_name = 'Organization'

    def ready(self):
        import capitolzen.organizations.signals  # noqa
