from celery import shared_task

from capitolzen.users.utils import get_intercom_client
from capitolzen.organizations.models import Organization
from intercom.errors import ResourceNotFound


@shared_task()
def intercom_manage_organization(organization_id, op):
    """
    Create, Update, Delete organization in intercom

    :param organization_id:
    :param op:
    :return:
    """

    intercom = get_intercom_client()

    if op != "delete":
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
        return intercom_company.id

    def _update():
        try:
            intercom_company = intercom.companies.find(
                company_id=str(organization.id))
            intercom_company = _populate_intercom_company(intercom_company)
            intercom.companies.save(intercom_company)
            return intercom_company.id
        except ResourceNotFound:
            _create()

    def _delete():
        try:
            intercom_company = intercom.companies.find(
                company_id=str(organization_id))
            intercom.companies.delete(intercom_company)
            return intercom_company.id
        except ResourceNotFound:
            pass

    if op == "create":
        _create()
    elif op == "update":
        _update()
    elif op == "delete":
        _delete()

    return True
