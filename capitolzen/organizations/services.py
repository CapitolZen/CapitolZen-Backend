from intercom.errors import ResourceNotFound
from stripe.error import StripeError
from capitolzen.users.utils import get_intercom_client
from django.conf import settings
from capitolzen.organizations.utils import get_stripe_client

from logging import getLogger
logger = getLogger('app')


class IntercomOrganizationSync(object):
    """

    """
    intercom = None
    organization = None
    organization_id = None

    def __init__(self):
        self.intercom = get_intercom_client()

    def build_resource_data(self):
        return {
            'name': self.organization.name,
            'custom_attributes': {
                'Status': self.organization.is_active,
                'Billing Name': self.organization.billing_name,
                'Billing Email': self.organization.billing_email,
                'Billing Phone': self.organization.billing_phone,
                'Billing Address One': self.organization.billing_address_one,
                'Billing Address Two': self.organization.billing_address_two,
                'Billing City': self.organization.billing_city,
                'Billing State': self.organization.billing_state,
                'Billing Zip': self.organization.billing_zip_code,
            },
        }

    def _create_or_update(self):
        """

        :return:
        """
        try:
            intercom_company = self.intercom.companies.find(
                company_id=str(self.organization.id))
        except ResourceNotFound:
            intercom_company = self.intercom.companies.create(
                company_id=str(self.organization.id),
                remote_created_at=self.organization.created.timestamp()
            )

        # Rebuild the intercom object.
        data = self.build_resource_data()
        for key in data:
            setattr(intercom_company, key, data[key])
        self.intercom.companies.save(intercom_company)

        logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % ("create_or_update", intercom_company.id))
        return {'op': 'create_or_update', 'id': intercom_company.id}

    def _delete(self):
        """

        :return:
        """
        logger.debug(" -- INTERCOM ORG SYNC - %s - %s" % ("delete", self.organization_id))
        try:
            intercom_company = self.intercom.companies.find(company_id=str(self.organization_id))
            self.intercom.companies.delete(intercom_company)
            return {'op': 'delete', 'id': self.organization_id}
        except ResourceNotFound:
            logger.debug(" -- INTERCOM ORG SYNC - Could not delete %s" % self.organization_id)
            return False

    def execute(self, organization, operation):
        """

        :param organization:
        :param operation:
        :return:
        """

        if operation != "delete":
            self.organization = organization
            self.organization_id = organization.id
        else:
            self.organization = None
            self.organization_id = organization

        if operation == "create_or_update":
            return self._create_or_update()
        elif operation == "delete":
            return self._delete()


class StripeOrganizationSync(object):
    """

    """
    stripe = None
    organization = None
    organization_id = None

    def __init__(self):
        self.stripe = get_stripe_client()

    def build_resource_data(self):
        owner = self.organization.owner.organization_user.user

        return {
            'description': self.organization.name,
            'email': owner.username if owner else None,
            'metadata': {
                'id': self.organization.id
            }
        }

    def _create(self):

        customer = self.stripe.Customer.create(**self.build_resource_data())

        if customer:
            self.organization.stripe_customer_id = customer.get('id')

            # Also subscribe them to the free plan.
            subscription = self.stripe.Subscription.create(
                customer=self.organization.stripe_customer_id,
                items=[
                    {
                        "plan": settings.STRIPE_DEFAULT_PLAN_ID,
                    },
                ]
            )
            self.organization.plan_name = settings.STRIPE_DEFAULT_PLAN_ID
            self.organization.stripe_subscription_id = subscription.get('id')
            self.organization.save()
            return customer
        else:
            return False

    def _create_or_update(self):
        try:
            if self.organization.stripe_customer_id:
                customer = self.stripe.Customer.retrieve(self.organization.stripe_customer_id)
            else:
                customer = self._create()

        except StripeError:
            # TODO: Make more specific to customer cannot be found.
            customer = self._create()

        data = self.build_resource_data()

        for key in data:
            setattr(customer, key, data[key])

        customer.save()
        return customer

    def _delete(self):
        try:
            cu = self.stripe.Customer.retrieve(self.organization_id)
            cu.delete()
        except StripeError:
            return False

    def execute(self, organization, operation):
        """

        :param organization:
        :param operation:
        :return:
        """

        if operation != "delete":
            self.organization = organization
            self.organization_id = organization.id
        else:
            self.organization = None
            self.organization_id = organization

        if operation == "create_or_update":
            return self._create_or_update()
        elif operation == "delete":
            return self._delete()
