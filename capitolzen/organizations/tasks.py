from celery import shared_task

from intercom.errors import ResourceNotFound

from stripe.error import StripeError

from capitolzen.users.utils import get_intercom_client
from capitolzen.organizations.models import Organization
from capitolzen.organizations.utils import get_stripe_client

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task()
def intercom_manage_organization(organization_id, operation):
    """
    Create, Update, Delete organization in intercom

    :param organization_id:
    :param op:
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

    def _create():
        intercom_company = intercom.companies.create(
            company_id=str(
                organization.id),
            name=organization.name,
            remote_created_at=organization.created.timestamp())
        intercom_company = _populate_intercom_company(intercom_company)
        intercom.companies.save(intercom_company)
        logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % (operation, intercom_company.id))

        return {'op': 'create', 'id': intercom_company.id}

    def _update():
        try:
            intercom_company = intercom.companies.find(
                company_id=str(organization.id))
            intercom_company = _populate_intercom_company(intercom_company)
            intercom.companies.save(intercom_company)
            logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % (operation, intercom_company.id))
            return {'op': 'update', 'id': intercom_company.id}
        except ResourceNotFound:
            _create()

    def _delete():
        try:
            intercom_company = intercom.companies.find(
                company_id=str(organization_id))
            intercom.companies.delete(intercom_company)
            logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % (operation, intercom_company.id))
            return {'op': 'delete', 'id': intercom_company.id}
        except ResourceNotFound:
            pass

    if operation == "create":
        return _create()
    elif operation == "update":
        return _update()
    elif operation == "delete":
        return _delete()

    return False


@shared_task()
def stripe_manage_customer(organization_id, operation):
    """
    Create, Update, Delete customer in stripe...
    Customer in stripe == Organization on our end.

    :param organization_id:
    :param op:
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
            cu = stripe.Customer.retrieve(organization.stripe_customer_id)
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
