from json import dumps, loads

from celery import shared_task
from django.conf import settings

from capitolzen.meta.clients import aws_client
from capitolzen.meta.notifications import email_user_report_link
from capitolzen.proposals.models import Wrapper
from capitolzen.proposals.utils import normalize_data
from capitolzen.users.models import User
from capitolzen.groups.models import Report

REPORT_FUNCTION = "capitolzen_search_reportify"


@shared_task
def generate_report(report):
    wrappers = Wrapper.objects.filter(group=report.group)
    filters = report.prepared_filters()
    if filters:
        wrappers = wrappers.filter(**filters)

    bill_list = normalize_data(wrappers)
    data = {
        "title": report.title,
        "id": str(report.id),
        "summary": report.description,
        "bills": bill_list,
    }

    logo_path = report.preferences.get("logo", False)

    if logo_path == 'organization':
        data["logo"] = report.organization.logo

    if logo_path == 'group':
        data['logo'] = report.group.logo

    layout = report.preferences.get('layout', False)
    if layout:
        data['layout'] = layout

    event = {
        "data": data,
        "bucket": settings.AWS_BUCKET_NAME,
        "organization": str(report.organization.id),
        "group": str(report.group.id),
    }
    event = dumps(event)
    func = aws_client("lambda")
    res = func.invoke(FunctionName=REPORT_FUNCTION,
                      InvocationType="RequestResponse",
                      Payload=event,
                      )

    status = res.get('StatusCode', False)

    if status != 200:
        return False
    response = res['Payload'].read()
    response = loads(response)

    url = response.get('url', False)
    if url:
        update_report_docs(report, url)

    return url


@shared_task
def email_report(report, user):
    report = Report.objects.get(pk=report)
    user = User.objects.get(pk=user)
    url = generate_report(report)
    print(report)
    if not url:
        return False
    else:
        email_user_report_link(
            to=user.username, report_title=report.title, url=url
        )


def update_report_docs(report, new_url):
    attachments = getattr(report, 'attachments')
    attachments['output_url'] = new_url
    setattr(report, 'attachments', attachments)
    report.save()
