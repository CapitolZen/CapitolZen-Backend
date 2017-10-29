from celery import shared_task

from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)

from capitolzen.proposals.utils import iterate_states, summarize


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


@shared_task(retry_kwargs={'max_retries': 10})
def summarize_proposal(identifier):
    from capitolzen.proposals.documents import BillDocument
    from capitolzen.proposals.models import Bill

    document = BillDocument.get(id=identifier)
    instance = Bill.objects.get(id=identifier)
    if document:
        instance.content = document.body.replace(
            '\n', ' ').replace(
            '\r', '').replace(
            '\xa0', ' ').strip()
        instance.summary = summarize(instance.content)
    else:
        raise summarize_proposal.retry(countdown=30)
