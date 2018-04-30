from celery import shared_task

from datetime import datetime, timedelta

from capitolzen.users.models import User, Action
from capitolzen.users.services import IntercomUserSync
from capitolzen.users.notifications import email_user_magic_link
from capitolzen.users.utils import token_encode

from django.conf import settings
from templated_email import send_templated_mail

from capitolzen.proposals.models import Event, Bill, Wrapper
from capitolzen.groups.models import Page


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
            bill=bill,
            title='bill:introduced',
            priority=0
        )
        a.save()

    for event in Event.objects.filter(time__gte=today, time__lt=next_week):
        a = Action.objects.create(
            user=user,
            event=event,
            priority=-1,
            title='committee:meeting'
        )
        a.save()

@shared_task
def create_daily_summary():
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    for user in User.objects.filter(is_active=True, page_viewer_users=None):

        bill_count = Bill.objects.filter(created__gt=yesterday).count()

        # bill_count = p.number_to_words(bill_count)
        bills = "%s New Introduced Bills" % bill_count

        wrapper_count = Wrapper.objects.filter(organization__users=user, bill__created__gt=yesterday).count()
        # wrapper_count = p.number_to_words(wrapper_count)
        wrappers = "%s Updated Saved Bills" % wrapper_count

        committee_count = Action.objects.filter(user=user, title='committee:meeting', created__gt=yesterday).count()
        committees = "%s Committee Meetings" % committee_count


        if bill_count or wrapper_count or committee_count:
            copy = "<p>You have updates! View your Capitol Zen account to see the latest updates. "
            copy += "You have:</p>"

            if bill_count:
                copy += '<p><strong>%s</strong></p>' % bills
            if wrapper_count:
                copy += '<p><strong>%s</strong></p>' % wrappers
            if committee_count:
                copy += '<p><strong>%s</strong></p>' % committees

            copy += '<p>View your Capitol Zen To Do list to review everything new in one place!</p>'

            url = "%s/dashboard" % settings.APP_FRONTEND

            context = {
                "message": copy,
                "subject": "Your Capitol Zen Daily Update",
                "action_cta": "View Now",
                "action_url": url,
            }
            try:
                send_templated_mail(
                    template_name='simple_action',
                    from_email='CapitolZenUpdates@capitolzen.com',
                    recipient_list=[user.username],
                    context=context,
                )
            except Exception:
                continue


@shared_task
def update_user_sync():
    for user in User.objects.filter(is_active=True):
        intercom_manage_user(user.id, 'update')

@shared_task
def generate_user_magic_link(user_id, page_id):
    try:
        user = User.objects.get(id=user_id)
        page = Page.objects.get(id=page_id)

        extra_context = {
            "token": token_encode(user, **{'organization_id': str(page.organization.id), 'page_id': str(page.id)}),
            "page_title": page.title,
            "reply_to": page.author.username,
            "author_name": page.author.name,
            "page_id": page_id
        }
        email_user_magic_link(user.username, **extra_context)


    except Exception as e:
        return e
