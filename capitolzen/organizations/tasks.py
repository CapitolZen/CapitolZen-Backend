from celery import shared_task
from capitolzen.organizations.models import Organization
from capitolzen.organizations.services import (
    ChargebeeOrganizationSync,
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
    if operation != "delete":
        organization = Organization.objects.get(id=organization_id)
    else:
        organization = organization_id

    return IntercomOrganizationSync().execute(organization, operation)


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
    if operation != "delete":
        organization = Organization.objects.get(id=organization_id)
    else:
        organization = organization_id

    return StripeOrganizationSync().execute(organization, operation)

@shared_task()
def chargebee_manage_customer(organization_id, operation):
    """
    Create, Update, Delete customer in stripe...
    Customer in stripe == Organization on our end.

    :param organization_id: when operation = delete, organization_id is actually
    the stripe customer id.
    :param operation: create_or_update || delete
    :return:
    """
    if operation != "delete":
        organization = Organization.objects.get(id=organization_id)
    else:
        organization = organization_id

    return ChargebeeOrganizationSync().execute(organization, operation)
