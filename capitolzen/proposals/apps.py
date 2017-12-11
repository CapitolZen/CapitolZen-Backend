from __future__ import unicode_literals

from django.apps import AppConfig


class ProposalsConfig(AppConfig):
    name = 'capitolzen.proposals'
    label = 'proposals'
    verbose_name = 'Proposals'

    def ready(self):
        import capitolzen.proposals.signals  # noqa
