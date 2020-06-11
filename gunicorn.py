"""gunicorn WSGI server configuration."""

from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count()


# bind = '0.0.0.0:' + environ.get('PORT', '5050')
bind = 'unix:/tmp/psdash.sock'
umask = 7
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()
access_logfile = 'gunicorn_access.log'
error_logfile = 'gunicorn_error.log'
