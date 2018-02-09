from celery import shared_task
import inflect

from datetime import datetime, timedelta
from django.utils import timezone

from capitolzen.users.models import User, Action
from capitolzen.users.services import IntercomUserSync
from django.conf import settings
from templated_email import send_templated_mail

from capitolzen.proposals.models import Event, Bill, Wrapper
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


@shared_task
def create_daily_summary():
    today = datetime.today()

    for user in User.objects.filter(is_active=True):

        bill_count = Bill.objects.filter(created__gte=today).count()

        # bill_count = p.number_to_words(bill_count)
        bills = "%s new bills" % bill_count

        wrapper_count = Wrapper.objects.filter(organization__users=user, bill__updated__gte=today)
        # wrapper_count = p.number_to_words(wrapper_count)
        wrappers = "%s updated bills" % wrapper_count

        committee_count = Action.objects.filter(user=user, title='committee:meeting', created__gte=today).count()
        committees = "%s committee meetings" % committee_count

        if bill_count or wrapper_count or committee_count:
            copy = "<p>You have updates! View your Capitol Zen account to see the latest updates.<p>"
            copy += "<p>You have:"
            if bill_count:
                copy += bills + ', '
            if wrapper_count:
                copy += wrappers + ', '
            if committee_count:
                copy += committees
            copy += '.</p>'

            url = "%s/dashboard" % settings.APP_FRONTEND

            context = {
                "message": copy,
                "subject": "Your Capitol Zen Daily Update",
                "action_cta": "View Now",
                "action_url": url,
            }

            send_templated_mail(
                template_name='simple_action',
                from_email='hello@capitolzen.com',
                recipient_list=user.username,
                context=context,
            )

@shared_task
def update_user_sync():
    for user in User.objects.filter(is_active=True):
        intercom_manage_user(user.id, 'update')
