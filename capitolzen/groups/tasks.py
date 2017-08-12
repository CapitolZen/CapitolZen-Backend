from json import dumps, loads
from celery import shared_task
from django.conf import settings
from capitolzen.meta.clients import aws_client
from capitolzen.meta.notifications import send_report
from capitolzen.proposals.models import Wrapper
from capitolzen.users.models import User
from .models import Report

REPORT_FUNCTION = "capitolzen_search_reportify"


@shared_task
def generate_report(report):
    wrappers = Wrapper.objects.filter(group=report.group)
    bill_list = normalize_data(wrappers)
    data = {
        "title": report.title,
        "id": str(report.id),
        "summary": report.description,
        "bills": bill_list
    }
    logo_path = report.preferences.get("logo", False)

    if logo_path:
        data["logo"] = getattr(report, logo_path)

    event = {
        "data": data,
        "bucket": settings.AWS_BUCKET_NAME,
        "organization": str(report.organization.id),
        "group": str(report.group.id)
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
    if not url:
        return False
    else:
        send_report(user, url)


def update_report_docs(report, new_url):
    attachments = getattr(report, 'attachments')
    doc_list = getattr(report, 'reportlist', [])

    curr_url = attachments.get('output_url', False)
    if curr_url:
        doc_list.append(curr_url)

    attachments['output_url'] = new_url
    attachments['reportlist'] = doc_list

    setattr(report, 'attachments', attachments)
    report.save()


def normalize_data(wrapper_list):
    output = []
    for w in wrapper_list:
        data = {
            "state_id": w.bill.state_id,
            "state": w.bill.state,
            "id": str(w.id),
            "sponsor": w.display_sponsor,
            "summary": w.display_summary,
            "current_committee": w.bill.current_committee,
            "status": w.bill.status,
            "position": w.position,
            "position_detail": w.position_detail,
            "last_action_date": w.bill.last_action_date
        }
        output.append(data)
    return output
