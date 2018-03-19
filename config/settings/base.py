"""
Django settings for downdraft-web project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import re
import environ
import datetime
from celery.schedules import crontab
from django.utils import six
from corsheaders.defaults import default_headers

# (capitolzen/config/settings/base.py - 3 = capitolzen/)
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('capitolzen')

env = environ.Env()
env.read_env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

# noinspection PyPackageRequirements
THIRD_PARTY_APPS = [
    'cacheops',
    'django_filters',
    'django_extensions',
    'localflavor',
    'corsheaders',
    'rest_framework',
    'rest_framework_jwt',
    'rest_framework_swagger',
    'dry_rest_permissions',
    'annoying',
    'storages',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'rest_auth',
    'stream_django',
    'django_elasticsearch_dsl'
]

ADMIN_APPS = [
    'material',
    'material.admin',
    'django.contrib.admin',
]

LOCAL_APPS = [
    'capitolzen.meta.apps.MetaConfig',
    'capitolzen.users.apps.UsersConfig',
    'capitolzen.organizations.apps.OrganizationsConfig',
    'capitolzen.groups.apps.GroupsConfig',
    'capitolzen.proposals.apps.ProposalsConfig',
    #'capitolzen.es_ingest.apps.ESIngestConfig',
    #'capitolzen.document_analysis.apps.DocumentAnalysisConfig'
]

INSTALLED_APPS = DJANGO_APPS + ADMIN_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.middleware.ActiveOrganizationMiddleware',
    'config.middleware.PageAccessMiddleWare',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
# Sparkpost email
SPARKPOST_KEY = env("SPARKPOST_API_KEY", default='')

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'
TEMPLATED_EMAIL_TEMPLATE_DIR = 'emails/'
TEMPLATED_EMAIL_FILE_EXTENSION = 'html'



# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""Donald and Matt""", 'donald@capitolzen.com'),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///capitolzen'),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True


# Cache
# ------------------------------------------------------------------------------
REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL',
                                      default='redis://redis:6379'), 0)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwenz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHEOPS_REDIS = '{0}/{1}'.format(
    env('REDIS_URL', default='redis://127.0.0.1:6379'), 2)

CACHEOPS_DEFAULTS = {
    'timeout': 60*60
}

CACHEOPS = {
    'users.user': {'ops': 'get', 'timeout': 60*60},
    'organizations.organization': {'ops': 'all', 'timeout': 60*60},
}


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Detroit'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

SECRET_KEY = env("APPLICATION_SECRET_KEY", default="")

CI = env("CI", default=False)

# Frontend Domain
APP_FRONTEND = env("APP_FRONTEND", default='')


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

AWS_ACCESS_KEY_ID = env('AWS_ACCESSID', default="")
AWS_SECRET_ACCESS_KEY = env('AWS_SECRETKEY', default="")
AWS_STORAGE_BUCKET_NAME = env('AWS_BUCKET_NAME', default="")
AWS_AUTO_CREATE_BUCKET = False
AWS_S3_CALLING_FORMAT = "path"
AWS_DEFAULT_ACL = 'private'
AWS_QUERYSTRING_AUTH = True

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIRY = 60 * 60 * 24 * 7

# TODO See: https://github.com/jschneier/django-storages/issues/47
# Revert the following and use str after the above-mentioned bug is fixed in
# either django-storage-redux or boto
AWS_HEADERS = {
    'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (
        AWS_EXPIRY, AWS_EXPIRY))
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


MEDIA_URL = 'https://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# REST FRAMEWORK
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'PAGE_SIZE': 20,
    'ORDERING_PARAM': 'sort',
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework_json_api.pagination.PageNumberPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_json_api.parsers.JSONParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=3),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_ALLOW_REFRESH': True,
}

JSON_API_FORMAT_KEYS = 'dasherize'
JSON_API_FILTER_KEYWORD = 'filter\[(?P<field>\w+)\]'

# I suppose technically this is some mix of auth + api
REST_USE_JWT = True
JWT_ALLOW_REFRESH = True

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

CORS_ORIGIN_WHITELIST = (
    'app.capitolzen.com',
    'capitolzen.com',
    'localhost:4200',
    'localhost:3000',
)

# methods allowed within CORS
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)

CORS_ALLOW_HEADERS = default_headers + (
    'X-Organization',
    'X-Page',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# Location of root django.contrib.admin.py URL, use {% url 'admin.py:index' %}
ADMIN_URL = r'^admin/'
API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


# CELERY
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('capitolzen.tasks.celery.CeleryConfig',)
CELERY_BROKER_URL = '{0}/{1}'.format(
    env('REDIS_URL', default='redis://redis:6379'), 1)
CELERY_RESULT_BACKEND = None
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Detroit'

CELERY_BEAT_SCHEDULE = {
    'import_committee': {
        'task': 'capitolzen.proposals.tasks.spawn_committee_updates',
        'schedule': crontab(minute=0, hour=0, day_of_week='sun')
    },
    'import_legislators': {
        'task': 'capitolzen.proposals.tasks.spawn_legislator_updates',
        'schedule': crontab(minute=0, hour=3, day_of_week='sat')
    },
    'import_bills': {
        'task': 'capitolzen.proposals.tasks.spawn_bill_updates',
        'schedule': crontab(minute=0, hour=5)
    },
    'import_meetings': {
        'task': 'capitolzen.proposals.tasks.spawn_committee_meeting_updates',
        'schedule': crontab(minute=0, hour='4-21')
    },
    'create_intro_actions': {
        'task': 'capitolzen.users.tasks.create_daily_summary',
        'schedule': crontab(minute=0, hour=9)
    },
    'update_user_intercom_sync': {
        'task': 'capitolzen.users.tasks.update_user_sync',
        'schedule': crontab(minute=30, hour=10)
    },
    'cleanup_bills': {
        'task': 'capitolzen.proposals.tasks.clean_missing_sponsors',
        'schedule': crontab(minute=30, hour=6)
    },

}

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env("DJANGO_LOG_LEVEL", default='WARNING'),
        },
        'django.request': {
            'handlers': ['console'],
            'level': env("REQUEST_LOG_LEVEL", default='ERROR'),
        },
        'intercom.request': {
            'handlers': ['console'],
            'level': env("REQUEST_LOG_LEVEL", default='ERROR'),
        },
        'django.db': {
            'handlers': ['console'],
            'level': env("DB_LOG_LEVEL", default='ERROR'),
        },
        'app': {
            'handlers': ['console'],
            'level': env("APP_LOG_LEVEL", default='ERROR'),
        }
    },
}

# CONNECTIONS
# ------------------------------------------------------------------------------

# Neo4j GRAPH DATABASE
GRAPH_DATABASE = {
    "user": env('GRAPH_USERNAME', default="neo4j"),
    "password": env('GRAPH_PASSWORD', default="neo4jpw"),
    "host": env('GRAPH_HOST', default='neo4j'),
    "secure": env.bool("GRAPH_SECURE", default=False),
    "bolt": True,
    "bolt_port": env.int('GRAPH_PORT', default=7687)
}

# AWS
AWS_ACCESS_ID = env("AWS_ACCESSID", default='')
AWS_SECRET_KEY = env("AWS_SECRETKEY", default='')
AWS_REGION = env("AWS_REGION", default='us-east-1')
AWS_BUCKET_NAME = env("AWS_BUCKET_NAME", default='')
AWS_TEMP_BUCKET_NAME = env("AWS_TEMP_BUCKET_NAME", default='')
AWS_CUSTOMER_IMPORT_BUCKET_NAME = env("AWS_CUSTOMER_IMPORT_BUCKET", default='cz-customer-import')
INDEX_LAMBDA = env(
    "capitolzen_search_bills", default="capitolzen_search_bills")


CURRENT_SESSION = env("CURRENT_SESSION", default="2017-2018")

# OPEN STATES
OPEN_STATES_KEY = env("OPEN_STATES_KEY", default='')
OPEN_STATES_URL = env(
    "OPEN_STATES_URL", default='https://openstates.org/api/v1/')

# ELASTIC SEARCH
ELASTICSEARCH_DSL = {
    'default': {
        'hosts':
            env("ELASTIC_SEARCH_URL", default='elastic:changeme@elasticsearch')
    },
}

# HASHID
HASHID_FIELD_SALT = env("HASHID_FIELD_SALT", default="asdfasdfsadfsadfdsafdsa")

# SLACK
SLACK_URL = env("UPDRAFT_SLACK_URL", default='')

# INTERCOM
INTERCOM_ACCESS_TOKEN = env("INTERCOM_ACCESS_TOKEN", default="")
INTERCOM_ENABLE_SYNC = True

# STRIPE
STRIPE_ENABLE_SYNC = True
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_DEFAULT_PLAN_ID = "basic"
STRIPE_ACTIVE_PLANS = [
    'basic',
    'professional'
]
# STREAM
STREAM_API_KEY = env("STREAM_API_KEY", default="")
STREAM_API_SECRET = env("STREAM_API_SECRET", default="")
STREAM_FEED_MANAGER_CLASS = 'capitolzen.meta.stream.FeedManager'

# ASANA
ASANA_PAT = env("ASANA_PAT", default='')
ASANA_PROJECT = env("ASANA_PROJECT", default="497390564241002")
ASANA_ENABLE_SYNC = env("ASANA_ENABLE_SYNC", default=False)
ASANA_WORKSPACE = env("ASANA_WORKSPACE", default="313428278436952")

# TRIVIA
REST_PROXY = {
    'HOST': 'http://jservice.io/api/random?count=30',
    'ACCEPT_MAPS': {'text/html': 'application/json'}
}

# Summarizing & URL Blocking
# -----------------------------------------------------------------------------
DEFAULT_SENTENCE_COUNT = 7
DEFAULT_SUMMARY_LENGTH = 250
TIME_EXCLUSION_REGEX = re.compile(
    r'(1[012]|[1-9]):[0-5][0-9](\\s)?(?i)\s?(am|pm|AM|PM)')
URL_REGEX = r'\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu' \
            r'|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name' \
            r'|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar' \
            r'|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs' \
            r'|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu' \
            r'|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi' \
            r'|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs' \
            r'|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it' \
            r'|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk' \
            r'|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr' \
            r'|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz' \
            r'|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru' \
            r'|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su' \
            r'|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw' \
            r'|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za' \
            r'|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?' \
            r'\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s' \
            r']+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a" \
            r'-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop' \
            r'|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad' \
            r'|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|' \
            r'bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|' \
            r'ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|' \
            r'dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|' \
            r'gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|' \
            r'id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|' \
            r'kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|' \
            r'mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|' \
            r'ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|' \
            r'pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|' \
            r'Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|' \
            r'tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|' \
            r'vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))'
DEFAULT_EXCLUDE_SENTENCES = [
    "Story highlights", "#", "##", "Discover Dubai",
    "By ", "Caption", "caption", "photos:", "1 of ",
    'JPG', 'jpg', 'png', "PNG", "ID:", "(REUTERS)",
    "Image", "BREAKING", "FORM", "1.", "by",
    "FFFD", "Fuck", "Shit", "Ass", "Cunt", "Jizz",
    '[', ']', '{', '}', '*', 'Related Topics:',
    'related topics:', '+', '=', 'free',
    'RELATED ARTICLES',
    'Continue reading', 'http', 'GODDAMMIT', 'hr',
    'min', 'main story', 'main', '(', ')', '/', '\\',
    'Advertisement', 'Photo', 'Erectile Dysfunction'
]

DEFAULT_EXCLUDE_ARTICLES = [
    'Discover Dubai', 'become a millionaire',
    'Burn More Calories and Lose Weight',
    'Burn More Calories', 'Lose Weight',
    "lose weight",
    "No one wants to adopt Rory the cat: "
    "Called 'Cat Dracula' | Examiner.com",
    "Petition:", "petition:", "Petition",
    "Sex Positions", "sex positions", "Orgasm",
    "orgasm", "Fuck", "Shit", "Ass", "Cunt",
    "Jizz", 'free']
BLOCKED_SITE = ['wnd.com', 'nationalenquirer.com']
UNSUPPORTED_UPLOAD_SITES = ['theguardian.com', 'circleci.com', 'wnd.com']
COMPANY_ACRONYMS = [
    ('ABC', 'Abc'), ('CNN', 'Cnn'), ('CBS', 'Cbs'),
    ('MSNBC', 'Msnbc'), ('BBC', 'Bbc'), ('CBC', 'Cbc'), ('CBS', 'Cbs'),
    ('NBC', 'Nbc'), ('NYT', 'Nyt'), ('PBS', 'Pbs'),
    ('cnnpolitics.com', 'Cnnpolitics.com'),
    ('NPR', 'Npr'), ('N.P.R.', 'N.p.r'), ('N.P.R', 'N.p.r'), ('N.Y.T', 'N.y.t'),
    ('N.Y.T.', 'N.y.t.'), ('TYT', 'Tyt'), ('T.Y.T.', 'T.y.t.'), ('FBI', 'Fbi'),
    ('F.B.I', 'F.b.i'), ('F.B.I.', 'F.b.i.'), ('CIA', 'Cia'),
    ('C.I.A.', 'C.i.a.'), ('C.I.A', 'C.i.a'), ('NSA', 'Nsa'),
    ('N.S.A', 'N.s.a'), ('N.S.A.', 'N.s.a.'), ('NASA', 'Nasa'),
    ('N.A.S.A', 'N.a.s.a'), ('N.A.S.A.', 'N.a.s.a.'), ('FEMA', 'Fema'),
    ('F.E.M.A.', 'F.e.m.a.'), ('F.E.M.A', 'F.e.m.a'), ('DOJ', 'Doj'),
    ('D.O.J', 'D.o.j'), ('D.O.J.', 'D.o.j.'), ('CDC', 'Cdc'),
    ('C.D.C', 'C.d.c'), ('C.D.C.', 'C.d.c.'), ('HEPA', 'Hepa'),
    ('H.E.P.A', 'H.e.p.a'), ('H.E.P.A.', 'H.e.p.a.'), ('U.S.', 'U.s.'),
    ('US', 'Us'), ('USA', 'Usa'), ('U.S.A.', 'U.s.a.'), ('U.S.A', 'U.s.a'),
    ('APC', 'Apc'), ('PDP', 'Pdp'), ('ISIS', 'Isis'), ('.com', '.Com'),
    ('abc7.com', 'Abc7.com'), ('cnn.com', 'Cnn.com'), ('ft.com', 'Ft.com'),
    ('World War II', 'World War Ii'), ('World War I', 'World War i'),
    ('DC', 'Dc'), ('D.C.', 'D.c.'), ('DMV', 'Dmv'), ('DNC', 'Dnc'),
    ('RNC', 'Rnc'), ('D.N.C.', 'D.n.c.'), ('R.N.C.', 'R.n.c.'),
    ('PC', 'Pc'), ('P.C.', 'P.c.'), ('LGBT', 'Lgbt'),
    ('L.G.B.T.', 'L.g.b.t.'), ('L.G.B.T', 'L.g.b.t'),
    ('LA Times', 'La Times'), ('L.A. Times', 'L.a. Times'),
    ('9th', '9Th'), ('ITV', 'Itv'), ('DNA', 'Dna'),
    ('AG', 'Ag'),  (u'AL', u'Al'), (u'AK', u'Ak'),
    (u'AZ', u'Az'), (u'AR', u'Ar'), (u'CA', u'Ca'),
    (u'CO', u'Co'), (u'CT', u'Ct'), (u'DK', u'Dk'), (u'DE', u'De'),
    (u'DC', u'Dc'), (u'FL', u'Fl'), (u'GA', u'Ga'), (u'GU', u'Gu'),
    (u'HI', u'Hi'), (u'ID', u'Id'), (u'IL', u'Il'),
    (u'IA', u'Ia'), (u'KS', u'Ks'), (u'KY', u'Ky'),  (u'LA', u'La'),
    (u'MD', u'Md'), (u'MI', u'Mi'), ('NRA', 'Nra'), ('N.R.A.', 'N.r.a.'),
    ('N.R.A', 'N.r.a'), ('UN', 'Un'), ('U.N.', 'U.n.'), ('U.N', 'U.n'),
    ('UNICEF', 'Unicef'), ('U.N.I.C.E.F.', 'U.n.i.c.e.f.'),
    ('U.N.I.C.E.F', 'U.n.i.c.e.f'),
    (u'MN', u'Mn'), (u'MO', u'Mo'), (u'MT', u'Mt'),
    (u'NE', u'Ne'), (u'NV', u'Nv'), (u'NH', u'Nh'), (u'NJ', u'Nj'),
    (u'NM', u'Nm'), (u'NY', u'Ny'), (u'NC', u'Nc'), (u'ND', u'Nd'),
    (u'MP', u'Mp'), ('EU', 'Eu'), ('UK', 'Uk'), ('De', 'DE'),
    (u'OL', u'Ol'), (u'PA', u'Pa'), (u'PI', u'Pi'), (u'PR', u'Pr'),
    (u'RI', u'Ri'), (u'SC', u'Sc'), (u'SD', u'Sd'), (u'TN', u'Tn'),
    (u'TX', u'Tx'), (u'UT', u'Ut'), (u'VT', u'Vt'), (u'VI', u'Vi'),
    (u'VA', u'Va'), (u'WA', u'Wa'), (u'WV', u'Wv'), (u'WI', u'Wi'),
    (u'WY', u'Wy')
]


EXPLICIT_SITES = [
    'xvideos.com', 'xhamster.com', 'pornhub.com', 'xnxx.com',
    'redtube.com', 'youporn.com', 'tube8.com', 'youjizz.com',
    'hardsextube.com', 'beeg.com', 'motherless.com',
    'drtuber.com', 'nuvid.com', 'pornerbros.com',
    'spankwire.com', 'keezmovies.com', 'sunporno.com',
    'porn.com', '4tube.com', 'alphaporno.com', 'xtube.com',
    'pornoxo.com', 'yobt.com', 'tnaflix.com', 'pornsharia.com',
    'brazzers.com', 'extremetube.com', 'slutload.com',
    'fapdu.com', 'empflix.com', 'alotporn.com', 'vid2c.com',
    'Shufuni.com', 'cliphunter.com', 'xxxbunker.com',
    'madthumbs.com', 'deviantclip.com', 'twilightsex.com',
    'pornhost.com', 'fux.com', 'jizzhut.com', 'spankbang.com',
    'eporner.com', 'orgasm.com', 'yuvutu.com', 'kporno.com',
    'definebabe.com', 'secret.shooshtime.com', 'mofosex.com',
    'hotgoo.com', 'submityourflicks.com', 'xxx.com',
    'bigtits.com', 'media.xxxaporn.com', 'bonertube.com',
    'userporn.com', 'jizzonline.com', 'pornotube.com',
    'fookgle.com', 'free18.net', 'tub99.com', 'nonktube.com',
    'mastishare.com', 'tjoob.com', 'rude.com', 'bustnow.com',
    'pornrabbit.com', 'pornative.com', 'sluttyred.com',
    'boysfood.com', 'moviefap.com', 'lubetube.com',
    'submityourtapes.com', 'megafilex.com', 'hdpornstar.com',
    'al4a.com', 'stileproject.com', 'xogogo.com', 'filthyrx.com',
    'jizzbo.com', '5ilthy.com', '91porn.com',
    'lesbianpornvideos.com', 'eroxia.com', 'iyottube.com',
    'yourfreeporn.us', 'sexoasis.com', 'fucktube.com',
    'pornomovies.com', 'clearclips.com', 'moviesand.com',
    'tubixe.com', 'pornjog.com', 'sextv1.pl', 'desihoes.com',
    'pornupload.com', 'kosimak.com', 'videocasalinghi.com',
    'lubeyourtube.com', 'freudbox.com', 'moviesguy.com',
    'motherofporn.com', '141tube.com', 'my18tube.com',
    'bigupload.com xvds.com', 'fastjizz.com', 'tubeland.com',
    'ultimatedesi.net', 'teenporntube.com', 'tubave.com',
    'afunnysite.com', 'sexe911.com', 'megaporn.com',
    'porntitan.com', 'pornheed.com', 'youhot.gr',
    'videolovesyou.com', 'onlymovies.com', 'hdporn.net',
    'adultvideodump.com', 'suzisporn.com', 'xfilmes.tv',
    'pornwall.com', 'silverdaddiestube.com',
    'sextube.sweetcollegegirls.com', 'ipadporn.com',
    'youporns.org', 'movietitan.com', 'yaptube.com', 'jugy.com',
    'chumleaf.com', 'panicporn.com', 'milfporntube.com',
    'timtube.com', 'wetpussy.com', 'whoreslag.com',
    'xfapzap.com', 'xvideohost.com', 'tuberip.com',
    'dirtydirtyangels.com', 'bigerotica.com', 'pk5.net',
    'theamateurzone.info', 'triniporn.org', 'youbunny.com',
    'isharemybitch.com', 'morningstarclub.com', 'sexkate.com',
    'kuntfutube.com', 'porncor.com', 'thegootube.com',
    'tubeguild.com', 'fuckuh.com', 'tube.smoder.com',
    'zuzandra.com', 'nextdoordolls.com', 'myjizztube.com',
    'homesexdaily.com', 'thetend.com', 'yourpornjizz.com',
    'tgirls.com', 'pornwaiter.com', 'pornhub.pl',
    'nurglestube.com', 'brazzershdtube.com', 'upthevideo.com',
    'sexzworld.com', 'cuntest.com', 'ahtube.com',
    'free2peek.com', 'freeamatube.com', 'thexxxtube.net',
    'yazum.com', 'tubesexes.com', 'pornload.com', 'vankoi.com',
    'dailee.com', 'ejason21.com', 'openpunani.com',
    'porntubexl.nl', 'scafy.com', 'bangbull.com', 'vidxnet.com',
    'yteenporn.com', 'tubethumbs.com', 'faptv.com', 'nasty8.com',
    'maxjizztube.com', 'pornunder.com', '24h-porn.net',
    'xclip.tv', 'jerkersworld.com', 'desibomma.com',
    'jizzbox.com', 'theyxxx.com', 'bonkwire.com',
    'PornTelecast.com', 'pornsitechoice.com', 'yporn.tv',
    'girlsongirlstube.com', 'famouspornstarstube.com',
    'sexfans.org', 'youpornxl.com', 'rudeshare.com',
    'efuckt.com', 'koostube.com', 'amateursex.com',
    'moviegator.com', 'cobramovies.com', 'cantoot.com',
    'yourhottube.com', 'teentube18.com', 'youxclip.com',
    'flicklife.com', 'nastyrat.tv', 'freepornfox.com',
    'freeadultwatch.com', 'fucked.tv', 'sextube.si',
    'pornrater.com', 'wheresmygf.com', 'xfanny.com',
    'pornorake.com', 'untouched.tv', 'guppyx.com',
    'mylivesex.tv', 'pervaliscious.com', 'sex2ube.com',
    'suckjerkcock.com', 'netporn.nl', 'exgfvid.com',
    'koalaporn.com', 'bbhgvidz.com', 'evilhub.com',
    'celebritytubester.com', 'pornfish.com', 'jrkn.com',
    'bootyclips.com', 'tubeguide.info', 'realhomemadetube.com',
    'tokenxxxporn.com', 'pornvideoflix.com', 'sinfultube.net',
    'pornler.com', 'sharexvideo.com', '69youPorn.com',
    'submitmyvideo.com', 'kastit.com', 'pornini.com',
    'hd4sex.com', 'laftube.com', 'mosestube.com',
    'dutchxtube.com', 'porncastle.net', 'tubedatbooty.com',
    'pornvie.com', 'pornopantry.com', 'springbreaktubegirls.com',
    'tube4u.net', 'nsfwftw.com', 'pornozabava.com',
    'tgutube.com', 'celebritynudez.com', 'teeztube.com',
    'collegefucktube.com', 'adultvideomate.com',
    'porntubemoviez.com', 'bigjuggs.com', 'hornypickle.com',
    'mypornow.com', 'pushingpink.com', 'xxxshare.ru',
    'nuuporn.com', 'melontube.com', 'myamateurporntube.com',
    'soyouthinkyourapornstar.com', 'porntubestreet.com',
    'pornogoddess.com', 'cumsnroses.com', 'porntubeclipz.com',
    'lcgirls.com', 'housewifes.com', 'cactarse.com',
    'cumfox.com', 'tube17.com', 'teenbrosia.com',
    'lesbiantubemovies.com', 'xxxset.com', 'gagahub.com',
    'jugland.com', 'porntubesurf.com', 'freakybuddy.com',
    'sexdraw.com', 'sexovirtual.com', 'pornsmack.com',
    'gratisvideokijken.nl', 'eroticadulttube.com',
    'bharatporn.com', 'fmeporn.com', 'darkpost.com',
    'sexporndump.com', 'sexandporn.org', 'jezzytube.com',
    'justpornclip.com', 'xxxpornow.com', 'inseks.com',
    'freeporn777.com', 'porndisk.com', 'adultfunnow.com',
    'youporn.us.com', 'babecumtv.com',
    'girlskissinggirlsvideos.com', 'specialtytubeporn.com',
    'teentube.be', 'www.xvideos.com', 'www.xhamster.com',
    'www.pornhub.com', 'www.xnxx.com', 'www.redtube.com',
    'www.youporn.com', 'www.tube8.com', 'www.youjizz.com',
    'www.hardsextube.com', 'www.beeg.com', 'www.motherless.com',
    'www.drtuber.com', 'www.nuvid.com', 'www.pornerbros.com',
    'www.spankwire.com', 'www.keezmovies.com',
    'www.sunporno.com', 'www.porn.com', '4tube.com',
    'www.alphaporno.com', 'www.xtube.com', 'www.pornoxo.com',
    'www.yobt.com', 'www.tnaflix.com', 'www.pornsharia.com',
    'www.brazzers.com', 'www.extremetube.com',
    'www.slutload.com', 'www.fapdu.com', 'www.empflix.com',
    'www.alotporn.com', 'www.vid2c.com', 'www.Shufuni.com',
    'www.cliphunter.com', 'www.xxxbunker.com',
    'www.madthumbs.com', 'www.deviantclip.com',
    'www.twilightsex.com', 'www.pornhost.com', 'www.fux.com',
    'www.jizzhut.com', 'www.spankbang.com', 'www.eporner.com',
    'www.orgasm.com', 'www.yuvutu.com', 'www.kporno.com',
    'www.definebabe.com', 'secret.shooshtime.com',
    'www.mofosex.com', 'www.hotgoo.com',
    'www.submityourflicks.com', 'www.xxx.com', 'www.bigtits.com',
    'media.xxxaporn.com', 'www.bonertube.com',
    'www.userporn.com', 'www.jizzonline.com',
    'www.pornotube.com', 'www.fookgle.com', 'free18.net',
    'www.tub99.com', 'www.nonktube.com', 'www.mastishare.com',
    'www.tjoob.com', 'www.rude.com', 'www.bustnow.com',
    'www.pornrabbit.com', 'www.pornative.com',
    'www.sluttyred.com', 'www.boysfood.com', 'www.moviefap.com',
    'www.lubetube.com', 'www.submityourtapes.com',
    'www.megafilex.com', 'www.hdpornstar.com', 'www.al4a.com',
    'www.stileproject.com', 'www.xogogo.com', 'www.filthyrx.com',
    'www.jizzbo.com', '5ilthy.com', '91porn.com',
    'www.lesbianpornvideos.com', 'www.eroxia.com',
    'www.iyottube.com', 'yourfreeporn.us', 'www.sexoasis.com',
    'www.fucktube.com', 'www.pornomovies.com',
    'www.clearclips.com', 'www.moviesand.com', 'www.tubixe.com',
    'www.pornjog.com', 'sextv1.pl', 'www.desihoes.com',
    'www.pornupload.com', 'www.kosimak.com',
    'www.videocasalinghi.com', 'www.lubeyourtube.com',
    'www.freudbox.com', 'www.moviesguy.com',
    'www.motherofporn.com', '141tube.com', 'www.my18tube.com',
    'bigupload.com xvds.com', 'www.fastjizz.com',
    'www.tubeland.com', 'ultimatedesi.net',
    'www.teenporntube.com', 'www.tubave.com',
    'www.afunnysite.com', 'www.sexe911.com', 'www.megaporn.com',
    'www.porntitan.com', 'www.pornheed.com', 'youhot.gr',
    'www.videolovesyou.com', 'www.onlymovies.com', 'hdporn.net',
    'www.adultvideodump.com', 'www.suzisporn.com', 'xfilmes.tv',
    'www.pornwall.com', 'www.silverdaddiestube.com',
    'sextube.sweetcollegegirls.com', 'www.ipadporn.com',
    'youporns.org', 'www.movietitan.com', 'www.yaptube.com',
    'www.jugy.com', 'www.chumleaf.com', 'www.panicporn.com',
    'www.milfporntube.com', 'www.timtube.com',
    'www.wetpussy.com', 'www.whoreslag.com', 'www.xfapzap.com',
    'www.xvideohost.com', 'www.tuberip.com',
    'www.dirtydirtyangels.com', 'www.bigerotica.com', 'pk5.net',
    'theamateurzone.info', 'triniporn.org', 'www.youbunny.com',
    'www.isharemybitch.com', 'www.morningstarclub.com',
    'www.sexkate.com', 'www.kuntfutube.com', 'www.porncor.com',
    'www.thegootube.com', 'www.tubeguild.com', 'www.fuckuh.com',
    'tube.smoder.com', 'www.zuzandra.com',
    'www.nextdoordolls.com', 'www.myjizztube.com',
    'www.homesexdaily.com', 'www.thetend.com',
    'www.yourpornjizz.com', 'www.tgirls.com',
    'www.pornwaiter.com', 'pornhub.pl', 'www.nurglestube.com',
    'www.brazzershdtube.com', 'www.upthevideo.com',
    'www.sexzworld.com', 'www.cuntest.com', 'www.ahtube.com',
    'www.free2peek.com', 'www.freeamatube.com', 'thexxxtube.net',
    'www.yazum.com', 'www.tubesexes.com', 'www.pornload.com',
    'www.vankoi.com', 'www.dailee.com', 'www.ejason21.com',
    'www.openpunani.com', 'porntubexl.nl', 'www.scafy.com',
    'www.bangbull.com', 'www.vidxnet.com', 'www.yteenporn.com',
    'www.tubethumbs.com', 'www.faptv.com', 'www.nasty8.com',
    'www.maxjizztube.com', 'www.pornunder.com', '24h-porn.net',
    'xclip.tv', 'www.jerkersworld.com', 'www.desibomma.com',
    'www.jizzbox.com', 'www.theyxxx.com', 'www.bonkwire.com',
    'www.PornTelecast.com', 'www.pornsitechoice.com', 'yporn.tv',
    'www.girlsongirlstube.com', 'www.famouspornstarstube.com',
    'sexfans.org', 'www.youpornxl.com', 'www.rudeshare.com',
    'www.efuckt.com', 'www.koostube.com', 'www.amateursex.com',
    'www.moviegator.com', 'www.cobramovies.com',
    'www.cantoot.com', 'www.yourhottube.com',
    'www.teentube18.com', 'www.youxclip.com',
    'www.flicklife.com', 'nastyrat.tv', 'www.freepornfox.com',
    'www.freeadultwatch.com', 'fucked.tv', 'sextube.si',
    'www.pornrater.com', 'www.wheresmygf.com', 'www.xfanny.com',
    'www.pornorake.com', 'untouched.tv', 'www.guppyx.com',
    'mylivesex.tv', 'www.pervaliscious.com', 'www.sex2ube.com',
    'www.suckjerkcock.com', 'netporn.nl', 'www.exgfvid.com',
    'www.koalaporn.com', 'www.bbhgvidz.com', 'www.evilhub.com',
    'www.celebritytubester.com', 'www.pornfish.com',
    'www.jrkn.com', 'www.bootyclips.com', 'tubeguide.info',
    'www.realhomemadetube.com', 'www.tokenxxxporn.com',
    'www.pornvideoflix.com', 'sinfultube.net', 'www.pornler.com',
    'www.sharexvideo.com', '69youPorn.com',
    'www.submitmyvideo.com', 'www.kastit.com', 'www.pornini.com',
    'www.hd4sex.com', 'www.laftube.com', 'www.mosestube.com',
    'www.dutchxtube.com', 'porncastle.net',
    'www.tubedatbooty.com', 'www.pornvie.com',
    'www.pornopantry.com', 'www.springbreaktubegirls.com',
    'tube4u.net', 'www.nsfwftw.com', 'www.pornozabava.com',
    'www.tgutube.com', 'www.celebritynudez.com',
    'www.teeztube.com', 'www.collegefucktube.com',
    'www.adultvideomate.com', 'www.porntubemoviez.com',
    'www.bigjuggs.com', 'www.hornypickle.com',
    'www.mypornow.com', 'www.pushingpink.com', 'xxxshare.ru',
    'www.nuuporn.com', 'www.melontube.com',
    'www.myamateurporntube.com',
    'www.soyouthinkyourapornstar.com', 'www.porntubestreet.com',
    'www.pornogoddess.com', 'www.cumsnroses.com',
    'www.porntubeclipz.com', 'www.lcgirls.com',
    'www.housewifes.com', 'www.cactarse.com', 'www.cumfox.com',
    'www.tube17.com', 'www.teenbrosia.com',
    'www.lesbiantubemovies.com', 'www.xxxset.com',
    'www.gagahub.com', 'www.jugland.com', 'www.porntubesurf.com',
    'www.freakybuddy.com', 'www.sexdraw.com',
    'www.sexovirtual.com', 'www.pornsmack.com',
    'gratisvideokijken.nl', 'www.eroticadulttube.com',
    'www.bharatporn.com', 'www.fmeporn.com', 'www.darkpost.com',
    'www.sexporndump.com', 'sexandporn.org', 'www.jezzytube.com',
    'www.justpornclip.com', 'www.xxxpornow.com',
    'www.inseks.com', 'www.freeporn777.com', 'www.porndisk.com',
    'www.adultfunnow.com', 'youporn.us.com', 'www.babecumtv.com',
    'www.girlskissinggirlsvideos.com',
    'www.specialtytubeporn.com']
