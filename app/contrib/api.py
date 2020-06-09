"""
RESTful JSON-API Client
"""

import logging
import requests
from w3lib.url import urljoin
from w3lib.url import add_or_replace_parameter


logger = logging.getLogger(__name__)


class API:
    '''Class for RESTful API based on JSON'''

    def __init__(self, api_url, api_key, timeout=30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def get(self, endpoint, *, elem_id=None, **query):
        '''GET Request'''
        api_url = urljoin(self.api_url, endpoint)
        if elem_id is not None:
            api_url = urljoin(api_url + '/', str(elem_id))
        logger.info('GET request to: %s', api_url)
        api_url = add_or_replace_parameter(api_url, 'api_key', self.api_key)
        resp = requests.get(api_url, params=query, timeout=self.timeout)
        return resp.json()

    def post(self, endpoint, **data):
        '''POST Request'''
        api_url = urljoin(self.api_url, endpoint)
        logger.info('POST request to: %s Data: %r', api_url, data)
        api_url = add_or_replace_parameter(api_url, 'api_key', self.api_key)
        resp = requests.post(api_url, json=data, timeout=self.timeout)
        return resp.json()

    def put(self, endpoint, elem_id, **data):
        '''PUT Request'''
        api_url = urljoin(self.api_url, endpoint)
        api_url = urljoin(api_url + '/', str(elem_id))
        logger.info('PUT request to: %s Data: %r', api_url, data)
        api_url = add_or_replace_parameter(api_url, 'api_key', self.api_key)
        resp = requests.put(api_url, json=data, timeout=self.timeout)
        return resp.json()

    def delete(self, endpoint, elem_id):
        '''DELETE Request'''
        api_url = urljoin(self.api_url, endpoint)
        api_url = urljoin(api_url + '/', str(elem_id))
        logger.info('DELETE request to: %s', api_url)
        api_url = add_or_replace_parameter(api_url, 'api_key', self.api_key)
        resp = requests.delete(api_url)
        return resp.json()
