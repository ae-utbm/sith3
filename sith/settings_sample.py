"""
Django settings for sith project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import binascii
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEV_ENV = True

if (DEV_ENV):
    os.environ['HTTPS'] = "off"
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    os.environ['HTTPS'] = "on"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(4sjxvhz@m5$0a$j0_pqicnc$s!vbve)z+&++m%g%bjhlz4+g2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

SITE_ID = 4000

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_jinja',
    'rest_framework',
    'ajax_select',
    'core',
    'club',
    'subscription',
    'accounting',
    'counter',
    'eboutic',
    'launderette',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'sith.urls'

TEMPLATES = [
    {
        "NAME": "jinja2",
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "app_dirname": "templates",
            "newstyle_gettext": True,
            "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.contrib.messages.context_processors.messages",
                ],
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.with_",
                "jinja2.ext.i18n",
                "jinja2.ext.autoescape",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
            ],
            "filters": {
                "markdown": "core.templatetags.renderer.markdown",
            },
            "globals": {
                "can_edit_prop": "core.views.can_edit_prop",
                "can_edit": "core.views.can_edit",
                "can_view": "core.views.can_view",
                "get_subscriber": "subscription.views.get_subscriber",
                "settings": "sith.settings",
            },
            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },
            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sith.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

LANGUAGES = [
        ('en', _('English')),
        ('fr', _('French')),
        ]

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

PHONENUMBER_DEFAULT_REGION = "FR"

# Medias
MEDIA_ROOT = './data/'
MEDIA_URL = '/data/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Auth configuration

AUTH_USER_MODEL = 'core.User'
AUTH_ANONYMOUS_MODEL = 'core.models.AnonymousUser'
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/'
DEFAULT_FROM_EMAIL="bibou@git.an"

# Email
EMAIL_HOST="localhost"
EMAIL_PORT=25

SITH_URL = "ae-taiste.utbm.fr"
SITH_NAME = "AE taiste"

# AE configuration
SITH_MAIN_CLUB = {
        'name': "AE",
        'unix_name': "ae",
        'address': "6 Boulevard Anatole France, 90000 Belfort"
        }

# Bar managers
SITH_BAR_MANAGER = {
        'name': "BdF",
        'unix_name': "bdf",
        'address': "6 Boulevard Anatole France, 90000 Belfort"
        }

# Launderette managers
SITH_LAUNDERETTE_MANAGER = {
        'name': "Laverie",
        'unix_name': "laverie",
        'address': "6 Boulevard Anatole France, 90000 Belfort"
        }

# Define the date in the year serving as reference for the subscriptions calendar
# (month, day)
SITH_START_DATE = (8, 15) # 15th August

# Used to determine the valid promos
SITH_SCHOOL_START_YEAR = 1999

SITH_GROUPS = {
    'root': {
        'id': 1,
        'name': "Root",
    },
    'public': {
        'id': 2,
        'name': "Not registered users",
    },
    'accounting-admin': {
        'id': 3,
        'name': "Accounting admin",
    },
    'communication-admin': {
        'id': 4,
        'name': "Communication admin",
    },
    'counter-admin': {
        'id': 5,
        'name': "Counter admin",
    },
}

SITH_BOARD_SUFFIX="-bureau"
SITH_MEMBER_SUFFIX="-membres"

SITH_MAIN_BOARD_GROUP=SITH_MAIN_CLUB['unix_name']+SITH_BOARD_SUFFIX
SITH_MAIN_MEMBERS_GROUP=SITH_MAIN_CLUB['unix_name']+SITH_MEMBER_SUFFIX

SITH_ACCOUNTING_PAYMENT_METHOD = [
        ('CHECK', _('Check')),
        ('CASH', _('Cash')),
        ('TRANSFERT', _('Transfert')),
        ('CARD', _('Credit card')),
        ]

SITH_SUBSCRIPTION_PAYMENT_METHOD = [
        ('CHECK', _('Check')),
        ('CARD', _('Credit card')),
        ('CASH', _('Cash')),
        ('EBOUTIC', _('Eboutic')),
        ('OTHER', _('Other')),
        ]

SITH_SUBSCRIPTION_LOCATIONS = [
        ('BELFORT', _('Belfort')),
        ('SEVENANS', _('Sevenans')),
        ('MONTBELIARD', _('Montbéliard')),
        ('EBOUTIC', _('Eboutic')),
        ]

SITH_COUNTER_BARS = [
        (1, "MDE"),
        (2, "Foyer"),
        (35, "La Gommette"),
        ]

SITH_COUNTER_PAYMENT_METHOD = [
        ('CHECK', _('Check')),
        ('CASH', _('Cash')),
        ('CARD', _('Credit card')),
        ]

SITH_COUNTER_BANK = [
        ('OTHER', 'Autre'),
        ('SOCIETE-GENERALE', 'Société générale'),
        ('BANQUE-POPULAIRE', 'Banque populaire'),
        ('BNP', 'BNP'),
        ('CAISSE-EPARGNE', 'Caisse d\'épargne'),
        ('CIC', 'CIC'),
        ('CREDIT-AGRICOLE', 'Crédit Agricole'),
        ('CREDIT-MUTUEL', 'Credit Mutuel'),
        ('CREDIT-LYONNAIS', 'Credit Lyonnais'),
        ('LA-POSTE', 'La Poste'),
        ]

# Defines which product type is the refilling type, and thus increases the account amount
SITH_COUNTER_PRODUCTTYPE_REFILLING = 11

# Defines which product is the one year subscription and which one is the six month subscription
SITH_PRODUCT_SUBSCRIPTION_ONE_SEMESTER = 93
SITH_PRODUCT_SUBSCRIPTION_TWO_SEMESTERS = 94

# Subscription durations are in semestres
# Be careful, modifying this parameter will need a migration to be applied
SITH_SUBSCRIPTIONS = {
    'un-semestre': {
        'name': _('One semester'),
        'price': 15,
        'duration': 1,
    },
    'deux-semestres': {
        'name': _('Two semesters'),
        'price': 28,
        'duration': 2,
    },
    'cursus-tronc-commun': {
        'name': _('Common core cursus'),
        'price': 45,
        'duration': 4,
    },
    'cursus-branche': {
        'name': _('Branch cursus'),
        'price': 45,
        'duration': 6,
    },
    'cursus-alternant': {
        'name': _('Branch cursus'),
        'price': 30,
        'duration': 6,
    },
    'membre-honoraire': {
        'name': _('Honorary member'),
        'price': 0,
        'duration': 666,
    },
    'assidu': {
        'name': _('Assidu member'),
        'price': 0,
        'duration': 2,
    },
    'amicale/doceo': {
        'name': _('Amicale/DOCEO member'),
        'price': 0,
        'duration': 2,
    },
    'reseau-ut': {
        'name': _('UT network member'),
        'price': 0,
        'duration': 1,
    },
    'crous': {
        'name': _('CROUS member'),
        'price': 0,
        'duration': 2,
    },
    'sbarro/esta': {
        'name': _('Sbarro/ESTA member'),
        'price': 15,
        'duration': 2,
    },
# To be completed....
}

SITH_CLUB_ROLES = {
        10: _('President'),
        9: _('Vice-President'),
        7: _('Treasurer'),
        5: _('Communication supervisor'),
        4: _('Secretary'),
        3: _('IT supervisor'),
        2: _('Board member'),
        1: _('Active member'),
        0: _('Curious'),
        }

# This corresponds to the maximum role a user can freely subscribe to
# In this case, SITH_MAXIMUM_FREE_ROLE=1 means that a user can set himself as "Membre actif" or "Curieux", but not higher
SITH_MAXIMUM_FREE_ROLE=1

# Minutes to timeout the logged barmen
SITH_BARMAN_TIMEOUT=20

# ET variables
SITH_EBOUTIC_ET_URL = "https://preprod-tpeweb.e-transactions.fr/cgi/MYchoix_pagepaiement.cgi"
SITH_EBOUTIC_PBX_SITE = "1520411"
SITH_EBOUTIC_PBX_RANG = "01"
SITH_EBOUTIC_PBX_IDENTIFIANT = "650995411"
SITH_EBOUTIC_HMAC_KEY = binascii.unhexlify("0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF")
SITH_EBOUTIC_PUB_KEY = ""
with open('./sith/et_keys/pubkey.pem') as f:
    SITH_EBOUTIC_PUB_KEY = f.read()

# Launderette variables
SITH_LAUNDERETTE_MACHINE_TYPES = [('WASHING', _('Washing')), ('DRYING', _('Drying'))]
SITH_LAUNDERETTE_PRICES = {
        'WASHING': 1.0,
        'DRYING': 0.75,
        }

IS_OLD_MYSQL_PRESENT = False
OLD_MYSQL_INFOS = {
        'host': 'ae-db',
        'user': "my_user",
        'passwd': "password",
        'db': "ae2-db",
        'charset': 'utf8',
        'use_unicode': True,
        }
