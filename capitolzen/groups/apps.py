from __future__ import unicode_literals

from django.apps import AppConfig


class GroupsConfig(AppConfig):
    name = 'capitolzen.groups'
    label = 'groups'
    verbose_name = 'Groups'

    def ready(self):
        import capitolzen.groups.signals  # noqa
