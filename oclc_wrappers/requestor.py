import requests

from oclc_wrappers.urlmanager import Urls


class Requestor(object):

    def __init__(self, auth, urls):
        self.auth = auth
        self.url = Urls(urls)

    def send_request(self, action, url_params=None, query_params=None, data=None):
        raise NotImplementedError


class HMACRequest(Requestor):

    def __init__(self, auth, urls):
        """
        :param auth: An authorization object built from auth.py
        :param urls: A dict of urls with a url and verb property, see constants.py
        """
        super(HMACRequest, self).__init__(auth, urls)

    def send_request(self, action, url_params=None, query_params=None, data=None):
        """
        Send a request to a specified OCLC Web Service.

        :param action: Action corresponding to URLs in OCLC's web service documentation
        :param url_params: Parameters to be filled in in the base URL
        :param query_params: Parameters to add to a query string
        :param data: Any data that needs to be sent in the body of the request

        :return: A Requests response object
        """
        url = self.url.get_url(action,
                               url_params,
                               params=query_params)
        http_verb = self.url.get_http_verb(action)
        r = requests.request(http_verb,
                             url,
                             json=data,
                             headers=self.auth.get_header(http_verb, url))
        self.auth.set_etag(r)
        return r


class WSKeyLiteRequest(Requestor):

    def __init__(self, auth, urls):
        """
        :param auth: An authorization object built from auth.py
        :param urls: A dict of urls with a url and verb property, see constants.py
        """
        super(WSKeyLiteRequest, self).__init__(auth, urls)

    def send_request(self, action, url_params=None, query_params=None, data=None):
        """
        Send a request to a specified OCLC Web Service.

        :param action: Action corresponding to URLs in OCLC's web service documentation
        :param url_params: Parameters to be filled in in the base URL
        :param query_params: Parameters to add to a query string
        :param data: Any data that needs to be sent in the body of the request

        :return: A Requests response object
        """
        if query_params is None:
            query_params = {}
        query_params.update({'wskey': self.auth.key})
        url = self.url.get_url(action, url_params, params=query_params)
        return requests.get(url)
