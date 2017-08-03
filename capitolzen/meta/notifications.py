from sparkpost import SparkPost
from celery import shared_task


sp = SparkPost()


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
