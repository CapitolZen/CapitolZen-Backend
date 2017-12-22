from celery import shared_task

from datetime import datetime, timedelta

from intercom.errors import ResourceNotFound

from capitolzen.proposals.models import Event, Bill

from capitolzen.users.models import User, Action
from capitolzen.users.utils import get_intercom_client

from celery.utils.log import get_task_logger

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
        intercom_user.email = getattr(user, 'username', None)
        intercom_user.name = getattr(user, 'name', None)
        intercom_user.custom_attributes['Status'] = getattr(user, 'is_active', False)
        companies = []
        for organization in user.organizations_organization.all():
            companies.append({
                'company_id': str(organization.id)
            })
        intercom_user.companies = companies

        return intercom_user

    def _create_or_update():

        try:
            intercom_user = intercom.users.find(user_id=str(user.id))
        except ResourceNotFound:
            intercom_user = intercom.users.create(
                user_id=str(user.id),
                email=user.username
            )

        intercom_user = _populate_intercom_user(intercom_user)
        intercom.users.save(intercom_user)
        logger.debug(" -- INTERCOM USER SYNC - %s - %s" % (operation, intercom_user.id))
        return {'op': 'create_or_update', 'id': intercom_user.id}

    def _delete():
        try:
            intercom_user = intercom.users.find(user_id=str(user_id))
            intercom.users.delete(intercom_user)
            logger.debug(" -- INTERCOM USER SYNC - %s - %s" % (operation, intercom_user.id))
            return {'op': 'delete', 'id': intercom_user.id}
        except ResourceNotFound:
            pass

    if operation == "create_or_update":
        _create_or_update()
    elif operation == "delete":
        _delete()

    return True


@shared_task()
def user_action_defaults(user_id):
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        return False

    today = datetime.today()
    next_week = today + timedelta(days=7)
    for bill in Bill.objects.filter(created_at__gt=today):
        a = Action.objects.create(
            user=user,
            action_object=bill,
            title='bill:introduced',
            priority=0
        )
        a.save()

    for event in Event.objects.filter(time__gte=today, time__lt=next_week):
        a = Action.objects.create(
            user=user,
            action_object=event,
            priority=-1,
            title='committee:meeting'
        )
        a.save()
