from django.conf import settings


def get_stripe_client():
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def get_chargebee_client():
    import chargebee
    chargebee.configure(settings.CHARGEBEE_API_KEY, settings.CHARGEBEE_SITE)
    return chargebee
