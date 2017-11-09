from celery.utils.log import get_task_logger
from celery import shared_task

from intercom.errors import ResourceNotFound

from capitolzen.users.models import Notification, User
from capitolzen.users.utils import get_intercom_client

logger = get_task_logger(__name__)


@shared_task()
def intercom_manage_user(user_id, operation):
    """
    Create, Update, Delete user in intercom

    :param user_id:
    :param operation:
    :return:
    """

    intercom = get_intercom_client()

    if operation != "delete":
        user = User.objects.get(id=user_id)
    else:
        user = None

    def _populate_intercom_user(intercom_user):
        # provider_info = user.provider_info
        return intercom_user

    def _create():
        intercom_user = intercom.users.create(user_id=str(user.id),
                                              email=user.email
                                              )
        intercom_user = _populate_intercom_user(intercom_user)
        intercom.users.save(intercom_user)
        return intercom_user.id

    def _update():
        try:
            intercom_user = intercom.users.find(user_id=str(user.id))
            intercom_user = _populate_intercom_user(intercom_user)
            intercom.users.save(intercom_user)
            return intercom_user.id
        except ResourceNotFound:
            _create()

    def _delete():
        try:
            intercom_user = intercom.users.find(user_id=str(user_id))
            intercom.users.delete(intercom_user)
            return intercom_user.id
        except ResourceNotFound:
            pass

    if operation == "create":
        _create()
    elif operation == "update":
        _update()
    elif operation == "delete":
        _delete()

    return True


@shared_task()
def intercom_manage_user_companies(user_id):
    """
    Called when a user is either added or removed from any organization
    :param user_id:
    :return:
    """
    user = User.objects.get(id=user_id)
    intercom = get_intercom_client()

    try:
        intercom_user = intercom.users.find(user_id=str(user.id))
    except ResourceNotFound:
        return False

    companies = []

    for organization in user.organizations_organization.all():
        companies.append({
            'company_id': str(organization.id)
        })

    intercom_user.companies = companies
    intercom.users.save(intercom_user)


@shared_task
def create_notification_task(title, categories, bill):
    users = User.objects.all()

    for user in users:
        new_alert = Notification.objects.create(
            message='A new bill called ' + title + ' has been created.',
            user=user,
            # bill=bill
            # group='test',
            # organization='test'
        )

        new_alert.save()


@shared_task
def create_user_notification(user_id, message, reference=False):
    user = User.objects.get(pk=user_id)
    a = Notification.objects.create(user=user, message=message)

    if reference:
        a.references = reference
    a.save()
