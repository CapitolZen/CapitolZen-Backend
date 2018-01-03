from celery import shared_task
from capitolzen.organizations.services import (
    IntercomOrganizationSync,
    StripeOrganizationSync)

from logging import getLogger
logger = getLogger('app')


@shared_task()
def intercom_manage_organization(organization_id, operation):
    """
    Create, Update, Delete organization in intercom

    :param organization_id:
    :param operation:
    :return:
    """
    return IntercomOrganizationSync().execute(organization_id, operation)


@shared_task()
def stripe_manage_customer(organization_id, operation):
    """
    Create, Update, Delete customer in stripe...
    Customer in stripe == Organization on our end.

    :param organization_id: when operation = delete, organization_id is actually
    the stripe customer id.
    :param operation: create_or_update || delete
    :return:
    """
    return StripeOrganizationSync().execute(organization_id, operation)
