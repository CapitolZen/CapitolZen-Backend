from json import dumps, loads

from celery import shared_task
from django.conf import settings
from django.utils.text import slugify

from capitolzen.meta.clients import aws_client
from capitolzen.meta.notifications import email_user_report_link
from capitolzen.proposals.models import Wrapper
from capitolzen.proposals.utils import normalize_bill_data
from capitolzen.users.models import User
from capitolzen.groups.models import Report, Update
from capitolzen.users.utils import token_encode
from capitolzen.users.notifications import email_user_page_updates

REPORT_FUNCTION = "capitolzen_search_reportify"


@shared_task
def generate_report(report):
    wrappers = Wrapper.objects.filter(group=report.group)
    filters = report.prepared_filters()
    if filters:
        wrappers = wrappers.filter(**filters)

    sort = {"property": "state_id", "direction": "asc"}
    sort = report.preferences.get('ordering', sort)
    order_key = "bill__%s" % sort['property']
    if sort['direction'] == "desc":
        order_key = "-"+sort

    wrappers = wrappers.order_by(order_key)
    bill_list = normalize_bill_data(wrappers)

    data = {
        "title": report.title,
        "id": str(report.id),
        "summary": report.description,
        "bills": bill_list,
        "slug_title": slugify(report.title)
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


@shared_task
def notify_group_guests_of_update(update_id):
    update = Update.objects.get(id=update_id)
    context = {
        'author_name': update.user.name,
        'author_email': update.user.username,
        'page_id': update.page.id,
        'page_name': update.page.title
    }

    for user in update.group.guest_users.filter(is_active=True):
        token = token_encode(user, **{'organization_id': str(update.organization.id), 'page_id': str(update.page.id)})
        context['token'] = token
        email_user_page_updates(user.username, **context)
