import requests

from oclc_wrappers.urlmanager import MultipleUrls, SingleUrl
from oclc_wrappers.constants import PO_URLS, ITEM_URLS, WORLDCAT_RESOURCE_URLS, WORLDCAT_LIBRARY_URLS, CLASSIFY_URL, FUND_URLS


class Requestor:

    def send_request(self):
        raise NotImplementedError

    def update_start_index(self, amount_to_update):
        self.query_params['startIndex'] += amount_to_update

    def all_records_retrieved(self, total_records):
        return total_records < self.query_params['startIndex']


class HMACRequest(Requestor):

    def __init__(self, auth, action, params=None, data=None):
        self.auth = auth
        self.action = action
        self.query_params = params
        self.data = data
        self.url = MultipleUrls({})
        self.url_params = {}

    def send_request(self):
        self.auth.url = self.url.get_url(self.action,
                                         params=self.query_params,
                                         **self.url_params)
        http_verb = self.url.get_http_verb(self.action)
        r = requests.request(http_verb,
                             self.auth.url,
                             headers=self.auth.get_header(http_verb),
                             json=self.data)
        self.auth.set_etag(r)
        return r


class WSKeyLiteRequest(Requestor):

    def __init__(self, key, action, params=None):
        self.key = key
        self.action = action
        if params is None:
            self.query_params = {}
        else:
            self.query_params = params
        self.query_params.update({'wskey': self.key})
        self.url_params = {}
        self.url = MultipleUrls({})

    def send_request(self):
        url = self.url.get_url(self.action, **self.url_params)
        return requests.get(url, params=self.query_params)


class PORequest(HMACRequest):

    def __init__(self, auth, action, po_number=None, params=None, data=None):
        super(PORequest, self).__init__(auth, action, params, data)
        self.url_params = {'order': po_number}
        self.url = MultipleUrls(PO_URLS)


class ItemRequest(HMACRequest):

    def __init__(self, auth, action, po_number=None, item_number=None, params=None, data=None):
        super(ItemRequest, self).__init__(auth, action, params, data)
        self.url_params = {'order': po_number, 'item': item_number}
        self.url = MultipleUrls(ITEM_URLS)


class ClassifyRequest(Requestor):

    def __init__(self, params):
        self.query_params = params
        self.url = SingleUrl(CLASSIFY_URL)

    def send_request(self):
        return requests.get(self.url.get_url(self.query_params))


class WorldcatRequest(WSKeyLiteRequest):

    def __init__(self, key, action, params=None, number=None):
        super(WorldcatRequest, self).__init__(key, action, params)
        self.url = MultipleUrls(WORLDCAT_RESOURCE_URLS)
        self.url_params = {'number': number}


class WorldcatLibraryRequest(WSKeyLiteRequest):

    def __init__(self, key, action, symbol, number, params=None):
        super(WorldcatLibraryRequest, self).__init__(key, action, params)
        self.url = MultipleUrls(WORLDCAT_LIBRARY_URLS)
        self.url_params = {'number': number}
        self.query_params.update({'oclcsymbol': symbol})


class FundRequest(HMACRequest):

    def __init__(self, auth, action, inst_id, fund=None, budget=None, params=None):
        super(FundRequest, self).__init__(auth, action, params)
        self.url = MultipleUrls(FUND_URLS)
        self.url_params = {'inst_id': inst_id, 'fund': fund, 'budget': budget}

