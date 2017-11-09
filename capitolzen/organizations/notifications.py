from templated_email import send_templated_mail
from django.conf import settings


def email_member_invite(to, **extra_context):
    """
    When: A user is invited to an existing organization
    To: The user who was invited
    :param to:
    :param extra_context:
    :return:
    """
    if to is not list:
        to = [to]

    message = "<p>You've been invited to join %s on Capitol Zen.</p>" % extra_context['organization_name']

    context = {
        "message": message,
        "subject": "You've been invited to Capitol Zen",
        "action_cta": "Accept Invite",
        **extra_context
    }

    send_templated_mail(
        template_name='simple_action',
        from_email='hello@capitolzen.com',
        recipient_list=to,
        context=context,
    )


def email_owner_welcome(to, **extra_context):
    """
    When: A new organization is created
    To: The user who was invited
    :param to:
    :param extra_context:
    :return:
    """
    if to is not list:
        to = [to]

    context = {
        'url': settings.APP_FRONTEND,
        **extra_context
    }

    send_templated_mail(
        template_name='welcome',
        from_email='hello@capitolzen.com',
        recipient_list=to,
        context=context)


def email_update_bills(subject, message, organization, bills, **extra_context):
    context = {
        'url': settings.APP_FRONTEND,
        'subject': subject,
        'bills': bills,
        **extra_context
    }
    send_templated_mail(
        template_name='bill_list',
        from_email='hello@capitolzen.com',
        recipient_list=organization.users.all(),
        message=message,
        context=context
    )
