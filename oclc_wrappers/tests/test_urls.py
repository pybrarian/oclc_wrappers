from unittest import TestCase

from oclc_wrappers.urlmanager import Urls
from oclc_wrappers.constants import ITEM_URLS, CLASSIFY_URL


class TestUrls(TestCase):

    def setUp(self):
        self.many_url = Urls(ITEM_URLS)
        self.single_url = Urls(CLASSIFY_URL)

    def test_get_url_from_a_multiple(self):
        self.assertEqual('https://acq.sd00.worldcat.org/purchaseorders/PO-123/items',
                         self.many_url.get_url('create', url_params={'order': 'PO-123'}))

    def test_get_http_verb(self):
        self.assertEqual('POST', self.many_url.get_http_verb('create'))

    def test_multiple_with_parameters(self):
        self.assertEqual('https://acq.sd00.worldcat.org/purchaseorders/PO-123/items?test=test',
                         self.many_url.get_url('create', params={'test': 'test'}, url_params={'order': 'PO-123'}))

    def test_single_with_parameters(self):
        self.assertEqual('http://classify.oclc.org/classify2/Classify?test=test',
                         self.single_url.get_url('read', params={'test': 'test'}))

