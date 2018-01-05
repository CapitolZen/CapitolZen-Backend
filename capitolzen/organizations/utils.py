from django.conf import settings


def get_stripe_client():
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe
