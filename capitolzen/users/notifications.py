from templated_email import send_templated_mail
from django.conf import settings


def email_user_password_reset_request(to, **extra_context):
    """
    When: When a user attempts to reset their password
    To: The user who wants their password reset.
    :param to:
    :param extra_context:
    :return:
    """
    if to is not list:
        to = [to]

    message = "<p>You requested to reset your password.</p>"
    message += "<p>If you didn't request a new password, please respond to this email.</p>"

    url = "%s/reset/%s" % (settings.APP_FRONTEND, extra_context['token'])

    context = {
        "message": message,
        "subject": "Reset Capitol Zen Password",
        "action_cta": "Reset Password",
        "action_url": url,
        **extra_context
    }

    send_templated_mail(
        template_name='simple_action',
        from_email='hello@capitolzen.com',
        recipient_list=to,
        context=context,
    )
