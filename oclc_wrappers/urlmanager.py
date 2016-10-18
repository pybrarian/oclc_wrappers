import six


class URLs:

    @staticmethod
    def add_query_params(url, params):
        try:
            query = six.moves.urllib.parse.urlencode(params)
            full_url = '{url}?{query}'.format(url=url, query=query)
        except TypeError:
            full_url = url
        return full_url


class SingleUrl(URLs):

    def __init__(self, url):
        self.url = url

    def get_url(self, params=None):
        return self.add_query_params(self.url.url, params)

    def get_http_verb(self, action):
        return self.url.verb


class MultipleUrls(URLs):

    def __init__(self, url_map):
        self.url_map = url_map

    def get_url(self, action, params=None, **kwargs):
        url = self.url_map[action].url
        url = url.format(**kwargs)
        return self.add_query_params(url, params)

    def get_http_verb(self, action):
        return self.url_map[action].verb
