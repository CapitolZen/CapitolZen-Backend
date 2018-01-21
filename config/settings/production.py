from .base import *  # noqa
import os
import raven

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if APPLICATION_SECRET_KEY not in os.environ
SECRET_KEY = env('APPLICATION_SECRET_KEY')

# MISC PROD STUFF
# ------------------------------------------------------------------------------
# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Add Gunicorn to installed apps
INSTALLED_APPS += ['gunicorn', ]

# APM (Sentry)
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]

MIDDLEWARE = [
                 'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
                 'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware'
             ] + MIDDLEWARE

LOGGING['handlers']['sentry'] = {
    'level': 'WARNING',
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}

LOGGING['loggers']['raven'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

LOGGING['loggers']['sentry.errors'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

RAVEN_CONFIG = {
    'dsn': 'https://46fd843f9b054ff8bdaade23e410b64c:555632fe5cb8420f9a404d1803bfffcd@sentry.io/275179',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
}

# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['example.com', ])
# END SITE CONFIGURATION

# CACHE
# ------------------------------------------------------------------------------
# Redis apparently doesn't really do the muti-db thing much anymore
# works fine for local stuff but the recommended way now is to have
# multiple endpoints.

CACHES['default']['LOCATION'] = '{0}/{1}'.format(
    env('CACHE_APP_DEFAULT_URL', default='redis://redis:6379'), 0)

CACHEOPS_REDIS = '{0}/{1}'.format(env(
    'CACHE_APP_OPCACHE_URL', default='redis://127.0.0.1:6379'), 0)

CELERY_BROKER_URL = '{0}/{1}'.format(
    env('CACHE_APP_CELERY_URL', default='redis://redis:6379'), 0)

# Static Assets
# ------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# EMAIL
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['anymail', ]
EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
ANYMAIL = {
    "SPARKPOST_API_KEY": SPARKPOST_KEY,
}
DEFAULT_FROM_EMAIL = "hello@capitolzen.com"

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# Custom Admin URL, use {% url 'admin.py:index' %}
ADMIN_URL = env('DJANGO_ADMIN_URL')
