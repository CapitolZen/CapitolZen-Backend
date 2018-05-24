import shortuuid
from json import dumps, loads
from django.conf import settings
from django.utils.text import slugify
from capitolzen.meta.clients import aws_client
from capitolzen.proposals.models import Wrapper
from capitolzen.proposals.utils import normalize_bill_data



class GenerateReport(object):
    report_function = "capitolzen_search_reportify"
    default_sort = {"property": "state_id", "direction": "asc"}
    organization_id = None
    group_id = None
    default_layout = 'detail_list'

    def __init__(self, org_id=None, group_id=None):
        self.organization_id = org_id
        self.group_id = group_id

    def from_report(self, report):
        self.organization_id = str(report.organization.id)
        self.group_id = str(report.group.id)
        wrappers = Wrapper.objects.filter(group=report.group)
        filters = report.prepared_filters()
        sort = report.preferences.get('ordering', self.default_sort)
        queryset = self.apply_filters(wrappers, sort, filters)
        url = self.generate(queryset, report.title, str(report.id), report.preferences.get('layout', False))
        return url

    def from_group(self, group_id, title):
        print(group_id)
        wrappers = Wrapper.objects.filter(group__id=group_id)
        uid = shortuuid.uuid()
        url = self.generate(wrappers, title, uid)
        return url

    def from_wrappers(self, wrapper_list, title):
        queryset = Wrapper.objects.filter(id__in=wrapper_list)
        uid = shortuuid.uuid()
        url = self.generate(queryset, title, uid)
        return url

    @staticmethod
    def apply_filters(queryset, sort, filters={}):

        if filters:
            queryset = queryset.filter(**filters)

        order_key = "bill__%s" % sort['property']
        if sort['direction'] == "desc":
            order_key = "-" + sort

        queryset.order_by(order_key)
        return queryset


    @staticmethod
    def normalize(queryset):
        return normalize_bill_data(queryset)

    def generate(self, queryset, title, uid, description=None, layout=False):
        bill_list = self.normalize(queryset)
        data = {
            "title": title,
            "id": uid,
            "summary": description,
            "bills": bill_list,
            "slug_title": slugify(title),
            "layout": self.default_layout
        }

        if layout:
            data['layout'] = layout

        event = {
            "data": data,
            "bucket": settings.AWS_BUCKET_NAME,
            "organization": self.organization_id,
            "group": self.group_id,
        }
        event = dumps(event)
        func = aws_client("lambda")
        res = func.invoke(FunctionName=self.report_function,
                          InvocationType="RequestResponse",
                          Payload=event,
                          )
        status = res.get('StatusCode', False)

        if status != 200:
            return False
        response = res['Payload'].read()
        response = loads(response)
        print(response)

        return response.get('url', False)
