from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--org_id', type=str)
        parser.add_argument('--email', type=str)

    def handle(self, *args, **options):
        pass
