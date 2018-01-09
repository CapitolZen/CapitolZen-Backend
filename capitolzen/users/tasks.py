from celery import shared_task
import inflect

from datetime import datetime, timedelta

from intercom.errors import ResourceNotFound

from django.conf import settings
from templated_email import send_templated_mail

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


@shared_task
def create_daily_summary():
    today = datetime.today()
    p = inflect.engine()

    for user in User.objects.filter(is_active=True):
        bill_count = Action.objects.filter(user=user, title='bill:introduced', created__gte=today).count()
        # bill_count = p.number_to_words(bill_count)
        bills = "%s new bills" % bill_count

        wrapper_count = Action.objects.filter(user=user, title='wrapper:updated', created__gte=today).count()
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
