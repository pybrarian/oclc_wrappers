import xml.etree.ElementTree as ET
import re

from oclc_wrappers.constants import WORLDCAT_RESOURCE_URLS, WORLDCAT_LIBRARY_URLS
from oclc_wrappers.requestor import WSKeyLiteRequest


class WorldcatResource(object):

    def __init__(self, key, xml_response):
        self.key = key
        self.root = ET.fromstring(xml_response)
        self.ns = '{http://www.loc.gov/MARC21/slim}'
        self.publisher_field = self.set_publisher_field()
        self.title_statement = self.find('datafield[@tag="245"]')

    @property
    def oclc_number(self):
        try:
            return self.find('controlfield[@tag="001"]').text
        except AttributeError:
            field = self.find('datafield[@tag="019"]')
            return self.find('subfield[@code="a"]', parent=field).text

    @property
    def cataloging_language(self):
        forty_field = self.find('datafield[@tag="040"]')
        lan = self.find('subfield[@code="b"]', parent=forty_field)
        return lan.text

    @property
    def control_field_008(self):
        return self.find('controlfield[@tag="008"]').text

    @property
    def publisher(self):
        if self.publisher_field is None:
            self.publisher_field = self.find('datafield[@tag="264"]')
        publisher = self.find('subfield[@code="b"]',
                              parent=self.publisher_field)
        return publisher.text.strip()[:-1]  # remove ISBD comma at end of field

    @property
    def publication_date(self):
        date_regex = re.compile('\d+')
        pub_date = self.find('subfield[@code="c"]',
                             parent=self.publisher_field)
        try:
            text = re.search(date_regex, pub_date.text).group().strip()
        except AttributeError:
            text = ''
        return text

    @property
    def title(self):
        sub_a = self.find('subfield[@code="a"]',
                          parent=self.title_statement).text
        try:
            sub_b = self.find('subfield[@code="b"]', self.title_statement).text
        except AttributeError:
            sub_b = ''
        return '{a}{b}'.format(a=sub_a, b=sub_b)[:-2]  # remove ISBD / from end

    @property
    def authors(self):
        authors = self.find('subfield[@code="c"]',
                            parent=self.title_statement).text
        return authors[:-1]  # remove ISBD period from end

    @property
    def isbn(self):
        isbn_10_regex = re.compile('^\d{10}$')
        isbn_fields = self.root.findall('.//{ns}{elem}'.format(ns=self.ns, elem='datafield[@tag="020"]'))
        for isbn in isbn_fields:
            try:
                return re.search(isbn_10_regex,
                                 self.find('subfield[@code="a"]',
                                           parent=isbn).text
                                 ).group().strip()
            except AttributeError:
                pass
        else:
            return ''

    @property
    def isbn_10s(self):
        isbn_10_regex = re.compile('^\d{10}$')
        isbn_fields = self.root.findall('.//{ns}{elem}'.format(ns=self.ns, elem='datafield[@tag="020"]'))
        isbns = []
        for isbn in isbn_fields:
            try:
                isbns.append(re.search(isbn_10_regex,
                                       self.find('subfield[@code="a"]',
                                                 parent=isbn).text
                                       ).group().strip())
            except AttributeError:
                pass
        if isbns:
            return isbns
        else:
            return ''

    @property
    def id_code(self):
        return self.isbn

    def find(self, elem, parent=None):
        try:
            return parent.find('./{ns}{elem}'.format(ns=self.ns, elem=elem))
        except AttributeError:
            return self.root.find('.//{ns}{elem}'.format(ns=self.ns, elem=elem))

    def check_for_holdings(self, oclc_symbol):
        return check_holdings_by_oclc_number(self.key, self.oclc_number, oclc_symbol)

    def set_publisher_field(self):
        pf = self.find('datafield[@tag="260"]')
        if pf is None:
            pf = self.find('datafield[@tag="264"]')
        return pf


class WorldcatHoldings(object):

    def __init__(self, xml_response):
        self.root = ET.fromstring(xml_response)

    @property
    def has_holdings(self):
        are_there_holdings = True
        try:
            self.root.find('.//copiesCount').text
        except AttributeError:
            are_there_holdings = False
        return are_there_holdings


def worldcat_request(auth):
    return WSKeyLiteRequest(auth, WORLDCAT_RESOURCE_URLS)


def worldcat_library_request(auth):
    return WSKeyLiteRequest(auth, WORLDCAT_LIBRARY_URLS)


def get_resource_by_isbn(auth, isbn, query_params=None):
    if query_params is None:
        query_params = {}
    query_params.update({'servicelevel': 'full'})
    url_params = {'number': isbn}
    requestor = worldcat_request(auth)
    r = requestor.send_request('isbn', url_params=url_params, query_params=query_params)
    return WorldcatResource(auth, r.content)


def check_holdings_by_oclc_number(auth, oclc_number, oclc_symbol, query_params=None):
    if query_params is None:
        query_params = {}
    query_params.update({'servicelevel': 'full', 'oclcsymbol': oclc_symbol})
    url_params = {'number': oclc_number}
    requestor = worldcat_library_request(auth)
    r = requestor.send_request('oclc', url_params=url_params, query_params=query_params)
    holdings = WorldcatHoldings(r.content)
    return holdings.has_holdings


def check_holdings_by_isbn(auth, isbn, oclc_symbol, query_params=None):
    if query_params is None:
        query_params = {}
    query_params.update({'servicelevel': 'full', 'oclcsymbol': oclc_symbol})
    url_params = {'number': isbn}
    requestor = worldcat_library_request(auth)
    r = requestor.send_request('isbn', url_params=url_params, query_params=query_params)
    holdings = WorldcatHoldings(r.content)
    return holdings.has_holdings
