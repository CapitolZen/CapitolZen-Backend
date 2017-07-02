from celery.utils.log import get_task_logger
from celery import shared_task
from .models import Alerts
from capitolzen.users.models import User

logger = get_task_logger(__name__)


@shared_task
def create_alert_task(title, categories):

    temp = categories
    users = User.objects.all()

    for user in users:
        new_alert = Alerts.objects.create(
            message='A new bill called ' + title + ' has been created.',
            user=user,
            # group='test',
            # organization='test'
        )

    new_alert.save()

