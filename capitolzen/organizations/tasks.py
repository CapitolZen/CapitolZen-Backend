from celery import shared_task

from intercom.errors import ResourceNotFound

from stripe.error import StripeError

from capitolzen.groups.models import Group, Report
from capitolzen.proposals.models import Wrapper

from capitolzen.users.utils import get_intercom_client
from capitolzen.organizations.models import Organization
from capitolzen.organizations.utils import get_stripe_client

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
    intercom = get_intercom_client()

    if operation != "delete":
        organization = Organization.objects.get(id=organization_id)
    else:
        organization = None

    def _populate_intercom_company(intercom_company):
        intercom_company.name = organization.name
        intercom_company.custom_attributes['Status'] = organization.is_active

        intercom_company.custom_attributes['Billing Name'] = \
            organization.billing_name
        intercom_company.custom_attributes['Billing Email'] = \
            organization.billing_email
        intercom_company.custom_attributes['Billing Phone'] = \
            organization.billing_phone
        intercom_company.custom_attributes['Billing Address One'] = \
            organization.billing_address_one
        intercom_company.custom_attributes['Billing Address Two'] = \
            organization.billing_address_two
        intercom_company.custom_attributes['Billing City'] = \
            organization.billing_city
        intercom_company.custom_attributes['Billing State'] = \
            organization.billing_state
        intercom_company.custom_attributes['Billing Zip'] = \
            organization.billing_zip_code

        return intercom_company

    def _create_or_update():
        try:
            intercom_company = intercom.companies.find(
                company_id=str(organization.id))
        except ResourceNotFound:
            intercom_company = intercom.companies.create(
                company_id=str(organization.id),
                remote_created_at=organization.created.timestamp()
            )

        intercom_company = _populate_intercom_company(intercom_company)
        intercom.companies.save(intercom_company)
        logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % (operation, intercom_company.id))
        return {'op': 'update', 'id': intercom_company.id}

    def _delete():
        logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % (operation, organization_id))
        from pprint import pprint
        try:
            intercom_company = intercom.companies.find(company_id=str(organization_id))
            pprint(intercom_company)
            intercom.companies.delete(intercom_company)
            return {'op': 'delete', 'id': organization_id}
        except ResourceNotFound:
            logger.debug(" -- INTERCOM ORG SYNC - Could not delete %s" % organization_id)
            pass

    if operation == "create_or_update":
        return _create_or_update()
    elif operation == "delete":
        return _delete()

    return False


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
    :param operation: create || update || delete
    :return:
    """

    stripe = get_stripe_client()

    if operation != "delete":
        organization = Organization.objects.get(id=organization_id)
    else:
        organization = None

    def _populate_stripe_customer():
        data = {
            'description': organization.name,
            'email': organization.owner_user_account().username,
            'metadata': {
                'id': organization.id
            }
        }

        return data

    def _create():

        customer = stripe.Customer.create(**_populate_stripe_customer())

        if customer:
            organization.stripe_customer_id = customer.get('id')
            organization.save()

        return customer

    def _update():
        try:
            cu = stripe.Customer.retrieve(organization.stripe_customer_id)
            data = _populate_stripe_customer()

            for key in data:
                setattr(cu, key, data[key])

            cu.save()
        except StripeError:
            pass

    def _delete():
        try:
            cu = stripe.Customer.retrieve(organization_id)
            cu.delete()
        except StripeError:
            pass

    if operation == "create":
        _create()
    elif operation == "update":
        _update()
    elif operation == "delete":
        _delete()

    return True
