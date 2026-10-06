import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из файла .env (не хранится в git)
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-@9txbhc45n*!dz$y#nd#x0nleysn&nja9l(-pn8elc!#-hk6yn",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0"
).split(",")

# origins для CSRF за прокси (Railway/Render завершают TLS до Django)
_csrf = [
    o.strip()
    for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
CSRF_TRUSTED_ORIGINS = _csrf

# корректное определение https за обратным прокси
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Безопасность (активируются только в продакшене, DEBUG=False) ---
if not DEBUG:
    # Редирект http -> https (работает корректно благодаря SECURE_PROXY_SSL_HEADER)
    SECURE_SSL_REDIRECT = True
    # Cookie только по https
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS: браузер будет ходить на сайт только по https в течение года
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Время жизни ссылки сброса пароля (по умолчанию в Django — 3 дня, слишком долго)
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 часа
# Время жизни сессии после входа (по умолчанию 2 недели — оставляем явно)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14


# Application definition

INSTALLED_APPS = [
    "modeltranslation",
    "authapp",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mainapp",
    "sorl.thumbnail",
    "mptt",
    "core",
    "crispy_forms",
    "crispy_bootstrap4",
    "django_filters",
    "django_countries",
    "taggit",
    "taggit_templatetags2",
    "subscribeapp",
    "axes",
    # django.contrib.sites обязателен для allauth
    "django.contrib.sites",
    # Вход через соцсети (django-allauth)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.yandex",
    "allauth.socialaccount.providers.facebook",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # django-axes: блокировка после N неудачных попыток входа (brute force)
    "axes.middleware.AxesMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

import dj_database_url

if os.environ.get("DATABASE_URL"):
    # Продакшен (например, Postgres на Railway): DATABASE_URL задаёт платформа
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Локальная разработка: SQLite (путь можно переопределить через SQLITE_PATH)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(os.environ.get("SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))),
        }
    }
# DATABASES = {     
# 		'default': {
#       	'ENGINE': 'django.db.backends.postgresql',
#       	'HOST' : os.environ.get('POSTGRES_HOST', 'localhost'),
#       	'NAME': os.environ.get('POSTGRES_DB', 'db_name'),
#       	'USER': os.environ.get('POSTGRES_USER', 'username'),
#       	'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
#       	'PORT': os.environ.get('POSTGRES_PORT', '5432'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Minsk"

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Список поддерживаемых языков
LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('be', _('Belarusian')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_URL = "/media/"
# На деплое указывается путь к примонтированному тому (например, /data/media)
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media")))
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

AUTH_USER_MODEL = "authapp.User"

# --- Защита от перебора паролей (django-axes) ---
# AxesStandaloneBackend обязан идти первым: он прерывает аутентификацию
# для заблокированных (слишком много неудачных попыток) пользователей
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    # allauth: аутентификация соц-аккаунтов (у них нет пароля)
    "allauth.account.auth_backends.AuthenticationBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # часов блокировки после превышения лимита
# Блокируем связку username+IP, а не IP целиком,
# чтобы не заблокировать офис/домашнюю сеть (NAT) из-за одного юзера
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
# Успешный вход сбрасывает счётчик неудачных попыток
AXES_RESET_ON_SUCCESS = True

LOGIN_REDIRECT_URL = "mainapp:main_page"
LOGOUT_REDIRECT_URL = "mainapp:main_page"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


# Настройки сервера исходящей почты (секреты берутся из .env / переменных окружения)
# Railway блокирует исходящий SMTP (25/465/587) — на проде письма шлём через
# HTTPS API Brevo. Если задан BREVO_API_KEY — используется API-бэкенд,
# иначе (локальная разработка) — обычный SMTP.
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
SENDPULSE_CLIENT_ID = os.environ.get("SENDPULSE_CLIENT_ID", "")
SENDPULSE_CLIENT_SECRET = os.environ.get("SENDPULSE_CLIENT_SECRET", "")
# Приоритет бэкендов (если EMAIL_BACKEND не задан явно): SendPulse API ->
# Brevo API -> SMTP (локальная разработка). SMTP на Railway не работает.
if not os.environ.get("EMAIL_BACKEND"):
    if SENDPULSE_CLIENT_ID and SENDPULSE_CLIENT_SECRET:
        EMAIL_BACKEND = "mainapp.services.email_api.SendPulseEmailBackend"
    elif BREVO_API_KEY:
        EMAIL_BACKEND = "mainapp.services.email_api.BrevoEmailBackend"
    else:
        EMAIL_BACKEND = "authapp.backends.email_backend.EmailBackend"
else:
    EMAIL_BACKEND = os.environ["EMAIL_BACKEND"]

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes")
# Таймаут SMTP-соединения (сек): без него недоступный SMTP подвешивает воркер
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "15"))
# Адрес отправителя писем (подписка, контактная форма).
# Должен быть подтверждён у почтового провайдера (SendPulse/Brevo)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "info@smarthata.by")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", SERVER_EMAIL)
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN", "")

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TAGGIT_TAG_CLOUD_ORDER_BY = '-num_times' # Сортировка облака тегов по частате


# --- Вход через соцсети (django-allauth) ---
SITE_ID = 1

# Активация email для соц-входов НЕ наша (у провайдера адрес уже проверен);
# наша собственная активация аккаунтов остаётся в authapp без изменений
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
# Локальный адаптер: username генерируется в пределах max_length=15
ACCOUNT_ADAPTER = "authapp.adapter.AccountAdapter"
# Адаптер соц-входа: активирует юзера сразу (см. authapp/adapter.py)
SOCIALACCOUNT_ADAPTER = "authapp.adapter.SocialAccountAdapter"
# Без промежуточной страницы "Продолжить": клик по кнопке соцсети
# сразу ведёт на страницу согласования провайдера
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # запрашиваем email-скоуп: он и есть логин в системе
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
}
