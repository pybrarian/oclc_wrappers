import six


class Urls:
    """
    Keep track of the various URLs and verbs for each web service.
    """

    def __init__(self, url_map):
        """
        :param url_map: Each web service should have a dict of URLs with
            actions as keys and objects with url and verb properties
        """
        self.url_map = url_map

    def get_url(self, action, url_params=None, params=None):
        """
        Pull the appropriate url and format it with url and query parameters

        :param action: Action corresponding to URLs in OCLC's web service documentation
        :param url_params: Parameters to be filled in in the base URL
        :param params: Parameters to add to a query string

        :return: A URL as a string with all necessary information
        """
        url = self.url_map[action].url
        url = url.format(**empty_object_if_none(url_params))
        return self.add_query_params(url, params)

    def get_http_verb(self, action):
        """Find the verb for the action."""
        return self.url_map[action].verb

    @staticmethod
    def add_query_params(url, params):
        """Add query parameters onto the end of a URL string."""
        try:
            query = six.moves.urllib.parse.urlencode(params)
            full_url = '{url}?{query}'.format(url=url, query=query)
        except TypeError:
            full_url = url
        return full_url


def empty_object_if_none(obj):
    """Utility function for null object pattern."""
    return {} if obj is None else obj
