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
        from_email='Capitol Zen Password <hello@capitolzen.com>',
        recipient_list=to,
        context=context,
    )


def email_user_magic_link(to, **extra_context):
    if to is not list:
        to = [to]
    message = "<p>You may now login by clicking the login button below.</p>"
    url = "%s/r?p=%s&token=%s" % (settings.APP_FRONTEND, extra_context['page_id'], extra_context['token'])
    context = {
        "message": message,
        "subject": "Login to access %s" % extra_context['page_title'],
        "action_cta": "Login",
        "action_url": url,
        **extra_context
    }

    kwargs = {
        "reply_to": extra_context["reply_to"]
    }
    from_email = '%s <hello@capitolzen.com>' % extra_context['author_name']

    send_templated_mail(
        template_name='simple_action',
        from_email=from_email,
        recipient_list=to,
        context=context,
        **kwargs
    )


def email_user_page_updates(to, **extra_context):
    """
    This email is automatically triggered to alert a guest user of a new updated post
    :param to:
    :param extra_context:
    :return:
    """

    if to is not list:
        to = [to]
    else:
        raise Exception()

    message = "<p>You have a new a new update published by %s at %s:</p>" % (extra_context['author_name'], extra_context['organization_name'])
    message += "<p><em><strong>%s<strong></em></p>" % extra_context['update_title']
    message += "<p>Click the link below to read the entire update.</p> "

    url = "%s/r?p=%s&u=%s&token=%s" % (settings.APP_FRONTEND, extra_context['page_id'], extra_context['update_id'], extra_context['token'])
    from_email = '%s <hello@capitolzen.com>' % extra_context['author_name']

    context = {
        "message": message,
        "subject": "New Updates from %s" % extra_context['author_name'],
        "action_cta": "Read Update",
        "action_url": url,
        **extra_context
    }

    kwargs = {
        "reply_to": extra_context["author_email"]
    }

    send_templated_mail(
        template_name='simple_action',
        from_email=from_email,
        recipient_list=to,
        context=context,
        **kwargs
    )
