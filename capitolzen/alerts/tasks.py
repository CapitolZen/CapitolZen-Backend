from celery.utils.log import get_task_logger
from celery import shared_task
from .models import Alerts

logger = get_task_logger(__name__)


@shared_task(name="create_alert_task")
def create_alert_task():

    new_alert = Alerts.objects.create(
            message='test alert time!'
        )

    # new_bill.serialize_history(data.history)
    # new_bill.serialize_categories(data.categories)
    new_alert.save()
