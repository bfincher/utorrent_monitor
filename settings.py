DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'torrents.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True

INSTALLED_APPS = (
    'data',
    )

SECRET_KEY = 'REPLACE_ME'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level' : 'DEBUG',
            'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : 'log.log',
            'maxBytes' : 1024*1024*10, # 10 MB
            'backupCount' : 5,
            'formatter' : 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        },
        'requests.packages.urllib3.connectionpool': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends' : {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
