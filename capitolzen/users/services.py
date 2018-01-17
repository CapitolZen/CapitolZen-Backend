from intercom.errors import ResourceNotFound
from capitolzen.users.models import User
from capitolzen.users.utils import get_intercom_client

from logging import getLogger
from capitolzen.users.models import Action
logger = getLogger('app')


class IntercomUserSync(object):
    """

    """
    intercom = None
    user = None
    user_id = None

    def __init__(self):
        self.intercom = get_intercom_client()

    def build_resource_data(self):
        data = {
            'email': self.user.username,
            'name': self.user.name,
            'companies': [],
            'custom_attributes': {
                'Status': self.user.is_active,
                'Active Actions': Action.objects.filter(user=self.user, state='active').count()
            }
        }

        companies = []

        companies = []
        for organization in self.user.organizations_organization.all():
            companies.append({
                'company_id': str(organization.id)
            })
        data['companies'] = companies
        return data

    def _create_or_update(self):
        try:
            intercom_user = self.intercom.users.find(user_id=str(self.user.id))
        except ResourceNotFound:
            intercom_user = self.intercom.users.create(
                user_id=str(self.user.id),
                email=self.user.username
            )

        # Rebuild the intercom object.
        data = self.build_resource_data()
        for key in data:
            setattr(intercom_user, key, data[key])
        self.intercom.users.save(intercom_user)

        logger.debug(" -- INTERCOM USER SYNC - %s - %s" % ("create_or_update", intercom_user.id))
        return {'op': 'create_or_update', 'id': intercom_user.id}

    def _delete(self):
        try:
            intercom_user = self.intercom.users.find(user_id=str(self.user_id))
            self.intercom.users.delete(intercom_user)
            logger.debug(" -- INTERCOM USER SYNC - %s - %s" % ("delete", intercom_user.id))
            return {'op': 'delete', 'id': intercom_user.id}
        except ResourceNotFound:
            return False

    def execute(self, user_id, operation):

        if operation != "delete":
            self.user = User.objects.get(id=user_id)
        else:
            self.user = None

        if operation == "create_or_update":
            return self._create_or_update()
        elif operation == "delete":
            return self._delete()
