from celery import shared_task
from capitolzen.organizations.models import Organization
from capitolzen.organizations.services import (
    IntercomOrganizationSync,
    StripeOrganizationSync)

from intercom.errors import ResourceNotFound

from capitolzen.groups.models import Group, Report
from capitolzen.proposals.models import Wrapper

from capitolzen.users.utils import get_intercom_client

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
def intercom_update_organization_attributes(organization_id):
    logger.debug('-- INTERCOM ORG STATS %s --' % organization_id)

    intercom = get_intercom_client()
    org = Organization.objects.get(id=organization_id)

    try:
        intercom_company = intercom.companies.find(company_id=str(org.id))
    except ResourceNotFound:
        intercom_company = intercom.companies.create(
            company_id=str(org.id),
            remote_created_at=org.created.timestamp()
        )

    intercom_company.custom_attributes['Report Count'] = Report.objects.filter(organization=org).count()
    intercom_company.custom_attributes['Active Group Count'] = Group.objects.filter(organization=org,
                                                                                    active=True).count()
    intercom_company.custom_attributes['Total Group Count'] = Group.objects.filter(organization=org).count()
    intercom_company.custom_attributes['Wrapper Count'] = Wrapper.objects.filter(organization=org).count()

    intercom.companies.save(intercom_company)
    return '-- INTERCOM ORG STATS %s --' % organization_id


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
