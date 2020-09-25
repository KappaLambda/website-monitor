from website_monitor.settings.base import *  # noqa: F401,F403

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}:{msecs}] - [{name}] - [{levelname}] - {message}',  # noqa: E501
            'datefmt': '%d/%m/%Y %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/website-monitor-tests.log',
            'mode': 'a',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
    },
}

RQ_QUEUES = {}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_website_monitor_db',
        'USER': 'test_user',
        'PASSWORD': 'test',
        'HOST': 'localhost',
        'PORT': '',
    },
}

# Public key of my private key used to sign the "fake" tokens
PUBLIC_KEY = (
    'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDM7h5HjdujzJpbTeM10lx2PGxWPcTa/tZM'
    '4a7iCddSGPce7Bb+ai4MSrZEh8wlW/AZNCJ6NcNydb/u1yfHqIWgbQeG7onftcBFtRe3Ew64'
    'xg03UGSFef1eeYnCkfFOgAq1dEXbLK8qqy74SeJTfjG07WPiNsKfZIn0pnVaKPSZM4AHFlAu'
    'AW5DQR+lqlk4nkG0Dld8geOqUSMxObd1Fr1odVm9z0W++KL4KOwaNLKhVEx32jclX9hQjovM'
    'WfFfu6Ro6bnhsq1rkJd6jxiP03xCyAQ12TThUVej1r6dTIDGULoFUFJN8CIPTwqaU0si89F2'
    'J6SDee9fbo+WG5Lek6j7xAJpHOQMhhUgvrDWPvzdDU1kVPOWJ7aJssakDnK+tq+PIh3QKToY'
    'mcjLUUpnhXqEsVv0z9G0AK/JC57YnescW591k2RfPMK5IXQr299X3L8g3eYREk7dnI8WtX9i'
    '5/YNZwxZZWAVAA1+PGPK0xzAEHJrMuPK4dkVDNea1+NpQwPrcAj4ztxHyAAJOL3b2XC+Hx57'
    'y6DORVlq8FLNQCzhk6tbhWOFNE4BNnpCRN80P/7i7gpaD+R7hXxJWKW1WnW4XSt3W5GEWLTo'
    'HVNjScmXu/kbm2l9QRoapXWYPJY7lHul6kw4lmO3tW98LrxpAW32g9b9jZo+9ehfgIeBPSrk'
    '9Q=='
)

JWT_AUTH['JWT_PUBLIC_KEY'] = PUBLIC_KEY  # noqa: F405
