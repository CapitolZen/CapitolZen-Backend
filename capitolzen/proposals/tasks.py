from celery import shared_task


from capitolzen.proposals.models import Bill
from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)

from capitolzen.proposals.utils import iterate_states, summarize
from capitolzen.proposals.documents import BillDocument


@shared_task
def bill_manager(state):
    return BillManager(state).run()


@shared_task
def legislator_manager(state):
    return LegislatorManager(state).run()


@shared_task
def committee_manager(state):
    return CommitteeManager(state).run()


@shared_task
def spawn_bill_updates():
    return iterate_states(BillManager, bill_manager)


@shared_task
def spawn_legislator_updates():
    return iterate_states(LegislatorManager, legislator_manager)


@shared_task
def spawn_committee_updates():
    return iterate_states(CommitteeManager, committee_manager)


@shared_task(retry_kwargs={'max_retries': 20})
def ingest_attachment(identifier):
    instance = Bill.objects.get(id=identifier)
    document = BillDocument.get(id=str(instance.id))
    if not document:
        raise ingest_attachment.retry(countdown=30)
    # Have to run save for some reason because python ES DSL doesn't invoke
    # the pipeline by default.
    document.save(pipeline="attachment")

    # Have to requery to get the new document with the attachment info included
    # .save() just returns a boolean so can't get the info from the response
    document = BillDocument.get(id=str(instance.id))
    instance.bill_text_analysis = document.bill_text_analysis.to_dict()
    instance.content = instance.bill_text_analysis.get('content', "").replace(
        '\n', ' ').replace(
        '\r', '').replace(
        '\xa0', ' ').strip()
    instance.summary = summarize(instance.content)
    instance.save()
    return True
