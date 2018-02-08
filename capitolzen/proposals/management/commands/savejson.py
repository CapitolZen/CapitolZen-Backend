from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
import requests
from json import load
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper


class Command(BaseCommand):
    help = 'Import dev data into the system'

    def handle(self, *args, **options):
        url = options.get('url', False)
        if not url:
            raise CommandError('must provide valid remote json source')
        org_id = options.get('org_id', False)
        if not org_id:
            raise CommandError("must provide valid org id")
        try:
            org = Organization.objects.get(id=org_id)
            data = self.fetch_json(url)
            keys = data.keys()
            print(keys)
            for key in keys:

                group, created = Group.objects.get_or_create(organization=org, title=key)
                for state_id in data[key]:
                    try:
                        bill = Bill.objects.get(state_id=state_id)
                        wrapper, wcreated = Wrapper.objects.get_or_create(
                            group=group,
                            bill=bill,
                            organization=org
                        )
                        if not wcreated:
                            self.stdout.write(self.style.WARNING("Wrapper already created for %s") % state_id)
                            continue
                        wrapper.save()
                        self.stdout.write(self.style.SUCCESS('wrapper created for %s') % state_id)

                    except ObjectDoesNotExist:
                        self.stdout.write(self.style.ERROR('Bill not found for %s') % state_id)

                continue
        except ObjectDoesNotExist:
            raise CommandError("invalid Org id")

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)
        parser.add_argument('--org_id', type=str)

    def fetch_json(self, url):
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                raise CommandError("Error Fetching Json")
        except Exception as e:
            raise CommandError("Error feting json %s" % e)


