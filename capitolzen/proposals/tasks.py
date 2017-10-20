from celery import shared_task

from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)
from capitolzen.proposals.utils import iterate_states


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
