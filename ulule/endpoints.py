class Endpoint(object):
    def __init__(self, master):
        self.master = master

    def get(self, slug):
        return self._request(self.path, slug)

    def list(self, *args, **kwargs):
        payload = {
            'offset': kwargs.get('offset', 0),
            'limit': kwargs.get('limit', 10),
        }

        payload.update(kwargs or {})

        paths = (self.path, ) + args

        return self._request(*paths, **payload)

    def _request(self, *args, **kwargs):
        return self.master.call('/'.join(args), kwargs)


class Users(Endpoint):
    path = 'users'

    def get_created_projects(self, username, *args, **kwargs):
        """
        Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        """

        kwargs['filter'] = 'created'
        return self.list(username, 'projects', *args, **kwargs)

    def get_followed_projects(self, username, *args, **kwargs):
        """
        Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        """

        kwargs['filter'] = 'followed'
        return self.list(username, 'projects', *args, **kwargs)

    def get_supported_projects(self, username, *args, **kwargs):
        """
        Projects created by the user

        Args:
            username (string): the username of the user
            offset (int): the offset of the query
            limit (int): the number of items to return (max 20)

        Returns:
            struct: struct of the project::
        """

        kwargs['filter'] = 'supported'
        return self.list(username, 'projects', *args, **kwargs)


class Projects(Endpoint):
    path = 'projects'

    def get_comments(self, slug, *args, **kwargs):
        return self.list(slug, 'comments', *args, **kwargs)

    def get_news(self, slug, *args, **kwargs):
        return self.list(slug, 'news', *args, **kwargs)

    def get_supporters(self, slug, *args, **kwargs):
        return self.list(slug, 'supporters', *args, **kwargs)


class News(Endpoint):
    path = 'news'

    def get_comments(self, pk, *args, **kwargs):
        return self.list(pk, 'comments', *args, **kwargs)


endpoints = [Users, Projects, News]
