import os
from pathlib import Path

# Asosiy yo'nalish yo'li
BASE_DIR = Path(__file__).resolve().parent.parent

# Xavfsizlik kaliti (Mahalliy ishlash uchun standart, Renderda o'zi Environment Variable'dan o'qiydi)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-w4btm2=#5x74=a@k4g-c)=f8w1ozl9m@z5u#728906c4xp(gqg')

# Serverda production rejimda ishlayotganini tekshirish (Render muhitida avtomatik False bo'ladi)
DEBUG = 'RENDER' not in os.environ

# Loyihaga kirish huquqiga ega hostlar listi
ALLOWED_HOSTS = ['*']

# WhiteNoise statik fayllar middleware'ni qo'shish uchun Render muhitida kerak
if not DEBUG:
    ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', '*')]


# Ilovalar ro'yxati
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'appointments', # Sizning asosiy ilovangiz
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Renderda statik fayllarni (CSS/JS) muammosiz o'qish uchun eng muhimi
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lor_navbat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lor_navbat.wsgi.application'


# Ma'lumotlar bazasi (SQLite serverda vaqtinchalik xotirada saqlanadi)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Parol xavfsizlik tekshiruvlari
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Til va Vaqt zonalari sozlamalari (O'zbekistonga moslangan)
LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# --- STATIK FAYLLAR (CSS, JS, RASMLAR) SOZLAMALARI (RENDER XATOLIGINI TUZATISH JOYI) ---
STATIC_URL = '/static/'

# Render talab qilgan, sizda yetishmayotgan asosiy qatorlar:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# WhiteNoise yordamida statik fayllarni siqish va keshga olish (Xatoliklarni oldini oladi)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'