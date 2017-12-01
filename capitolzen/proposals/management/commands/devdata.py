from django.core.management.base import BaseCommand, CommandError
from capitolzen.proposals.managers import BillManager
from capitolzen.meta.states import AVAILABLE_STATES


class Command(BaseCommand):
    help = 'Import dev data into the system'

    def handle(self, *args, **options):

        for state in AVAILABLE_STATES:
            BillManager(state.name).run()
