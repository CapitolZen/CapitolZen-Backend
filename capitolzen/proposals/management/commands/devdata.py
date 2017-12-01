from django.core.management.base import BaseCommand, CommandError
from capitolzen.proposals.managers import BillManager


class Command(BaseCommand):
    help = 'Import dev data into the system'

    def handle(self, *args, **options):
        BillManager('MI').run()

