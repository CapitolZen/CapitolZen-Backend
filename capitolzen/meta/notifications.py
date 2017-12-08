from logging import getLogger
from sparkpost import SparkPost
from celery import shared_task
from requests import post
from .clients import asana_client

from django.conf import settings

from templated_email import send_templated_mail


logger = getLogger('app_logger')


@shared_task
def alert_admin(message, priority=0):
    if priority > 1:
        admin_slack(message)
    else:
        admin_email(message)


@shared_task
def admin_slack(message):
    data = {
        "text": message
    }
    try:
        post(settings.SLACK_URL, data=data)
    except Exception as e:
        logger.info(e)


def email_user_report_link(to, **extra_context):
    """
    When: A user requests "email" report
    :param user:
    :param url:
    :return:
    """
    if to is not list:
        to = [to]

    message = "<p>You requested a copy of %s</p>" % extra_context['report_title']
    message += "<p>Click the button below or copy this link:</p>"
    message += "<p>%s</p>" % extra_context['url']

    context = {
        "message": message,
        "subject": "Download %s" % extra_context['report_title'],
        "action_cta": "Download Report",
        "action_url": extra_context['url'],
        **extra_context
    }

    send_templated_mail(
        template_name='simple_action',
        from_email='hello@capitolzen.com',
        recipient_list=to,
        context=context,
    )


@shared_task
def admin_email(message, subject=False):
    """
    TODO: Convert to templated email. see other examples.
    :param message:
    :param subject:
    :return:
    """

    recipients = ['djwasserman@gmail.com']
    html = "<p>%s<p>" % message
    sp = client()
    if not subject:
        subject = "Admin Alert"
    try:
        sp.transmissions.send(
            recpients=recipients,
            html=html,
            from_email='donald@capitolzen.com',
            subject=subject
        )
    except Exception:
        pass


@shared_task
def api_email(recpients, subject, message):
    """
    TODO: Convert to templated email. see other examples.
    :param message:
    :param subject:
    :return:
    """

    sp = client()
    sp.transmission.send(
        recpients=recpients,
        html=message,
        subject=subject,
        from_email='donald@capitolzen.com'
    )


def client():
    if not settings.CI:
        return SparkPost(api_key=settings.SPARKPOST_KEY)
    else:
        return False


def create_asana_task(title, description):
    if settings.ASANA_ENABLE_SYNC:
        aclient = asana_client()

        try:
            result = aclient.tasks.create_in_workspace(
                settings.ASANA_WORKSPACE,
                {'name': title, 'notes': description, 'projects': [settings.ASANA_PROJECT]}
            )
            return result
        except Exception as e:
            return e.__dict__
