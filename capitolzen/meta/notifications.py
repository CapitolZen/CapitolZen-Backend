from sparkpost import SparkPost
from celery import shared_task
from django.conf import settings
from requests import post

sp = SparkPost(settings.SPARKPOST_KEY)


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
    post(settings.SLACK_URL, data=data)


@shared_task
def admin_email(message, subject=False):
    recipients = ['dwasserman@capitolzen.com']
    html = "<p>%s<p>" % message
    if not subject:
        subject = "Admin Alert"
    sp.transmissions.send(
        recpients=recipients,
        html=html,
        from_email='donald@capitolzen.com',
        subject=subject
    )

