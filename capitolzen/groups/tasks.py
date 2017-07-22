from json import dumps, loads
from celery import shared_task
from capitolzen.meta.clients import aws_client
from capitolzen.proposals.models import Wrapper, Bill

REPORT_FUNCTION = "capitolzen_search_reportify"


@shared_task
def async_generate_report(report):
    url = generate_report(report)

    attachments = getattr(report, 'attachments')
    attachments['output_url'] = url
    setattr(report, 'attachements', attachments)
    report.save()


def generate_report(report):
    wrappers = Wrapper.objects.filter(group=report.group)
    bill_list = normalize_data(wrappers)
    data = {
        "title": report.title,
        "summary": report.summary,
        "bills": bill_list
    }

    event = dumps(data)
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
    return response['url']


def normalize_data(wrapper_list):
    output = []
    for w in wrapper_list:
        data = {
            "state_id": w.bill.state_id,
            "state": w.bill.state,
            "id": w.id,
            "sponsor": w.bill.sponsor,
            "summary": w.display_summary,
            "current_committee": w.bill.current_committee,
            "status": w.bill.status,
            "position": w.position,
            "position_detail": w.position_detail
        }
        output.append(data)
    return output
