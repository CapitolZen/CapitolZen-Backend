from django.core.management.base import BaseCommand, CommandError

import csv
from io import StringIO
from django.conf import settings

from capitolzen.utils.s3 import get_s3_resource
from common.utils.mobiledoc.utils import MobileDoc

from capitolzen.proposals.models import Bill, Wrapper
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group

resource = get_s3_resource()


class Command(BaseCommand):
    help = 'create wrappers for orgs based on csv'

    bucket = settings.AWS_CUSTOMER_IMPORT_BUCKET_NAME

    def get_file(self, key):
        s3 = resource.Bucket(self.bucket)
        obj = s3.Object(key=key)
        response = obj.get()

        if not response.get('Body', False):
            raise CommandError('error fetching file from s3')
        return response['Body'].read().decode('utf-8').splitlines()

    def add_arguments(self, parser):
        parser.add_argument('--key', type=str)
        parser.add_argument('--org_id', type=str)
        parser.add_argument('--group_id', type=str)

    def handle(self, *args, **options):
        if not options.get('key', False):
            raise CommandError('must provide valid s3 key')

        org_id = options['org_id']
        try:
            org = Organization.objects.get(id=org_id)
            groups = Group.objects.filter(organization=org).order_by('-created')
            group_id = options.get('group_id', False)
            if not group_id:
                group_id = getattr(groups.first(), 'id')
            group = groups.filter(id=group_id).first()

            contents = self.get_file(options['key'])
            del contents[0]
            reader = csv.reader(contents)
            for row in reader:

                try:
                    state_id = str(row[0])
                    bill = Bill.objects.get(state_id=state_id)
                    wrapper, created = Wrapper.objects.get_or_create(
                        bill=bill,
                        group=group,
                        organization=org,
                    )
                    if created:
                        if row[1]:
                            wrapper.summary = row[1]

                        position = row[2].lower().strip()
                        if position == 'support' or position == 'oppose':
                            wrapper.position = position

                        if row[3]:
                            doc = MobileDoc()
                            doc.add_p(row[3])
                            wrapper.notes = []
                            mobiledoc = doc.json()
                            wrapper.notes.append(mobiledoc)

                        wrapper.save()
                        print(wrapper.__dict__)
                except Exception:
                    self.stdout.write(self.style.ERROR('error finding %s' % row[0]))
                    continue

        except Exception:
            raise CommandError('Organization needs correct id %s' % org_id)
