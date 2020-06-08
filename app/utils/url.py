"""
Some utilities for URLs in the app
"""

from is_safe_url import is_safe_url as ext_is_safe_url

from app import psdash


def is_safe_url(url):
    '''Check if the URL is safe for redirection'''
    return ext_is_safe_url(url, psdash.config['APP_DOMAINS'])
