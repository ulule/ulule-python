'''
Wrap the Ulule API

Inspiration : Mailchimp API wraper
'''
import requests
import os.path
import logging
import sys
import time


class Error(Exception):
    pass

ERROR_MAP = {}

logger = logging.getLogger('ulule_mailchimp')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stderr))


class Ulule(object):
    root = 'https://api.ulule.com/v1/'
    last_request = {}

    def __init__(self, username=None, apikey=None, lang=None, debug=False):
        self.session = requests.session()
        if debug:
            self.level = logging.INFO
        else:
            self.level = logging.DEBUG

        if apikey is None:
            if 'ULULE_APIKEY' in os.environ:
                apikey = os.environ['ULULE_APIKEY']

        if apikey is None:
            raise Error('You must provide an Ulule API key')

        self.apikey = apikey

        if username is None:
            if 'ULULE_USERNAME' in os.environ:
                username = os.environ['ULULE_USERNAME']

        if username is None:
            raise Error('You must provide an Ulule username')

        self.username = username

        if lang is not None:
            self.lang = lang

        self.users = Users(self)
        self.projects = Projects(self)
        self.news = News(self)

    def call(self, url, payload=None):
        '''Actually make the API call with the given params
        this should only be called by the namespace methods
        use the helpers in regular usage like m.helper.ping()'''
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
                'user-agent': 'Ulule-Python/0.1',
                'Authorization': 'ApiKey %s:%s' % (self.username, self.apikey)
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
            raise self.cast_error(r)

        result = r.json()

        return result

    @staticmethod
    def cast_error(result):
        '''Take a result representing an error and cast it to a specific
        exception if possible (use a generic ulule.Error exception for
        unknown cases)'''
        if 'status' not in result\
                or result['status'] != 'error'\
                or 'name' not in result:
            raise Error('We received an unexpected error: %r' % result)

        if result['name'] in ERROR_MAP:
            return ERROR_MAP[result['name']](result['error'])
        return Error(result['error'])

    def log(self, *args, **kwargs):
        '''Proxy access to the ulule logger,
        changing the level based on the debug setting'''
        logger.log(self.level, *args, **kwargs)

    def __repr__(self):
        return '<Ulule %s>' % self.username


class Endpoint(object):
    def __init__(self, master):
        self.master = master

    @staticmethod
    def pagination_payload(offset=0, limit=20):
        return {
            'offset': offset,
            'limit': limit,
        }


class Users(Endpoint):
    path = 'users'

    def get(self, username):
        '''User information

        Args:
            username (string): the username of the user

        Returns:
            struct: struct of the user data::
                date_joined (string): the date of when the user joined
                id (int): the id of the user
                is_active (boolean): is the user active
                last_login (string): the date of when the user last login
                public_url (string): the public url of the user on ulule.com
                resource_uri (string): the api ressource uri
                username (string); the username of the user
        '''
        return self.master.call('%s/%s' % (self.path, username))

    def _projects(self, username, payload=None):
        return self.master.call('%s/%s/projects' % (self.path, username),
                                payload)

    def created_projects(self, username, offset=0, limit=20):
        '''Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        '''
        payload = self.pagination_payload(offset, limit)
        payload.update({'filter': 'created'})
        return self._projects(username, payload=payload)

    def followed_projects(self, username, offset=0, limit=20):
        '''Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        '''
        payload = self.pagination_payload(offset, limit)
        payload.update({'filter': 'followed'})
        return self._projects(username, payload=payload)

    def supported_projects(self, username, offset=0, limit=20):
        '''Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        '''
        payload = self.pagination_payload(offset, limit)
        payload.update({'filter': 'supported'})
        return self._projects(username, payload=payload)


class Projects(Endpoint):
    path = 'projects'

    def get(self, slug):
        return self.master.call('%s/%s' % (self.path, slug))

    def comments(self, slug, offset=0, limit=20):
        payload = self.pagination_payload(offset, limit)
        return self.master.call('%s/%s/comments' % (self.path, slug), payload)

    def news(self, slug, offset=0, limit=20):
        payload = self.pagination_payload(offset, limit)
        return self.master.call('%s/%s/news' % (self.path, slug), payload)

    def supporters(self, slug, offset=0, limit=20):
        payload = self.pagination_payload(offset, limit)
        return self.master.call('%s/%s/supporters' % (self.path, slug), payload)


class News(Endpoint):
    path = 'news'

    def get(self, nid):
        return self.master.call('%s/%s' % (self.path, nid))

    def comments(self, nid, offset=0, limit=20):
        payload = self.pagination_payload(offset, limit)
        return self.master.call('%s/%s/comments' % (self.path, nid), payload)
