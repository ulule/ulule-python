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


endpoints = [Users, Projects, News]
