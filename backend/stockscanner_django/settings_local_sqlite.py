from .settings import *  # noqa

# Use SQLite for local testing
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # type: ignore[name-defined]
    }
}

