from templated_email import send_templated_mail
from django.conf import settings


def email_group_contact_link(to, **extra_context):
    """
    When: When a user attempts to reset their password
    To: The user who wants their password reset.
    :param to:
    :param extra_context:
    :return:
    """

    if to is not list:
        to = [to]

    message = "<p>View the updates from %s.</p>" % extra_context['org_name']
    message += "<p>After clicking this link, you will automatically be logged in to view your updates.</p>"

    url = "%s/p/%s/%s" % (settings.APP_FRONTEND, extra_context['page_id'], extra_context['token'])

    context = {
        "message": message,
        "subject": "View Your Custom Page",
        "action_cta": "View",
        "action_url": url,
        **extra_context
    }

    send_templated_mail(
        template_name='simple_action',
        from_email='Capitol Zen <hello@capitolzen.com>',
        headers={'Reply-To': 'donald@capitolzen.com'},
        recipient_list=to,
        context=context,
    )
