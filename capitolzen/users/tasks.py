from celery.utils.log import get_task_logger
from celery import shared_task
from capitolzen.users.models import Notification, User

logger = get_task_logger(__name__)


@shared_task
def create_notification_task(title, categories, bill):

    temp = categories
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
