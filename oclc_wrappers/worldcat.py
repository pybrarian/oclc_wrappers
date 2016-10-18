import xml.etree.ElementTree as ET
import re

from .requestor import WorldcatRequest, WorldcatLibraryRequest


class WorldcatResource:

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
        isbn_10_regex = re.compile('^[0-9xX]{10}$')
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
        isbn_10_regex = re.compile('^[0-9xX]{10}$')
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


class WorldcatHoldings:

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


def get_resource_by_isbn(key, isbn, params=None):
    if params is None:
        params = {}
    params.update({'servicelevel': 'full'})
    requestor = WorldcatRequest(key, 'isbn', params=params, number=isbn)
    r = requestor.send_request()
    return WorldcatResource(key, r.content)


def check_holdings_by_oclc_number(key, oclc_number, oclc_symbol, params=None):
    if params is None:
        params = {}
    params.update({'servicelevel': 'full'})
    requestor = WorldcatLibraryRequest(key, 'oclc', oclc_symbol, params=params, number=oclc_number)
    r = requestor.send_request()
    holdings = WorldcatHoldings(r.content)
    return holdings.has_holdings
