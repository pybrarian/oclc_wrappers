import xml.etree.ElementTree as ET

from oclc_wrappers.requestor import ClassifyRequest
from oclc_wrappers.constants import NS


class Classify(object):

    def __init__(self, xml_response):
        self.root = ET.fromstring(xml_response)

    @property
    def response_code(self):
        code = self.root.find('classify:response', NS)
        return code.attrib['code']

    @property
    def most_holdings(self):
        try:
            editions = self.root.find('classify:editions', NS)
            return editions.find('classify:edition', NS).attrib
        except AttributeError:
            raise TypeError('Only Single-work records display most holdings information')


def get_full_by_isbn_number(isbn, **kwargs):
    params = {'isbn': isbn, 'summary': 'false'}
    for key, val in kwargs.items():
        params[key] = val
    requestor = ClassifyRequest(params)
    r = requestor.send_request()
    return Classify(r.content)
