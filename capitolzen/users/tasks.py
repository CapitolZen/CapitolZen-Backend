from celery import shared_task

from datetime import datetime, timedelta

from capitolzen.proposals.models import Event, Bill

from capitolzen.users.models import User, Action
from capitolzen.users.services import IntercomUserSync
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
    return IntercomUserSync().execute(user_id, operation)


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
