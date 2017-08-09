from celery.utils.log import get_task_logger
from celery import shared_task
from capitolzen.users.models import Alert, User

logger = get_task_logger(__name__)


@shared_task
def create_alert_task(title, categories, bill):

    temp = categories
    users = User.objects.all()

    for user in users:
        new_alert = Alert.objects.create(
            message='A new bill called ' + title + ' has been created.',
            user=user,
            # bill=bill
            # group='test',
            # organization='test'
        )

        new_alert.save()


@shared_task
def create_user_alert(user_id, message, reference=False):
    user = User.objects.get(pk=user_id)
    a = Alert.objects.create(user=user, message=message)

    if reference:
        a.references = reference
    a.save()
