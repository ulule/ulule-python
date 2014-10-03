'''
Wrap the Ulule API

Inspiration : Mailchimp API wraper
'''
import requests
import os.path
import logging
import sys
import time


ERROR_MAP = {}


default_logger = logging.getLogger('ulule')
default_logger.setLevel(logging.INFO)
default_logger.addHandler(logging.StreamHandler(sys.stderr))


from .endpoints import endpoints
from .exceptions import APIError
from . import __version__


def cast_error(result):
    """
    Take a result representing an error and cast it to a specific
    exception if possible (use a generic ulule.Error exception for
    unknown cases)
    """
    if ('status' not in result
            or result['status'] != 'error'
            or 'name' not in result):

        raise APIError('Unexpected error: %r' % result)

    if result['name'] in ERROR_MAP:
        return ERROR_MAP[result['name']](result['error'])

    return APIError(result['error'])


class Connection(object):
    root = 'https://api.ulule.com/v1/'
    last_request = {}

    def __init__(self, username=None, api_key=None, lang=None, logger=None):
        self.session = requests.session()

        self.logger = logger or default_logger

        api_key = os.environ.get('ULULE_API_KEY', api_key)

        if api_key is None:
            raise Exception('You must provide an Ulule API key')

        username = os.environ.get('ULULE_USERNAME', username)

        if username is None:
            raise Exception('You must provide an Ulule username')

        self.api_key = api_key
        self.username = username
        self.lang = lang

        for endpoint_class in endpoints:
            setattr(self, endpoint_class.path, endpoint_class(self))

    def call(self, url, payload=None):
        if payload is None:
            payload = {}

        if self.lang is not None:
            payload.update({'lang': self.lang})

        self.log('GET %s%s: %s' % (self.root, url, payload))
        start = time.time()

        r = self.session.get(
            '%s%s' % (self.root, url),
            params=payload,
            headers={
                'user-agent': 'Ulule-Python/%s' % __version__,
                'Authorization': 'ApiKey %s:%s' % (self.username, self.api_key)
            })
        try:
            # grab the remote_addr before grabbing the text
            # since the socket will go away
            remote_addr = r.raw._original_response.fp._sock.getpeername()
        except:
            # we use two private fields when getting the remote_addr,
            # so be a little robust against errors
            remote_addr = (None, None)

        complete_time = time.time() - start
        self.log('Received %s in %.2fms: %s' % (
            r.status_code,
            complete_time * 1000,
            r.text))
        self.last_request = {
            'url': url,
            'request_body': payload,
            'response_body': r.text,
            'remote_addr': remote_addr,
            'response': r,
            'time': complete_time
        }

        if r.status_code != requests.codes.ok:
            raise cast_error(r)

        result = r.json()

        return result

    def log(self, *args, **kwargs):
        """
        Proxy access to the ulule logger,
        changing the level based on the debug setting
        """
        self.logger.log(self.logger.level, *args, **kwargs)

    def __repr__(self):
        return '<Ulule %s:%s>' % (self.username, self.api_key)
