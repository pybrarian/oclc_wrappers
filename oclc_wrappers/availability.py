import xml.etree.ElementTree as ET

import requests


class Availability:

    def __init__(self, xml_response):
        self.root = ET.fromstring(xml_response)
        self.holdings = self.set_holdings(self.root)

    def set_holdings(self, root):
        return [Holding(holding) for holding in root.iter('holding')]

    @property
    def has_holdings(self):
        return len(self.holdings) > 0


class Holding:

    def __init__(self, holding):
        self.holding = self.set_holding(holding)

    def set_holding(self, holding):
        """
        Takes an XML Element object and recursively creates a plain Python
        object containing the data.

        :param holding: Element from xml.etree.ElementTree containing holdings
            information
        :return: An object containing a representation of the XML data
        """
        holdings = {}
        for elem in holding:
            if list(elem):  # library's way of saying node not an element
                holdings[elem.tag] = self.set_holding(elem)
            else:
                if elem.text:
                    holdings[elem.tag] = elem.text
                elif elem.attrib:
                    holdings[elem.tag] = elem.attrib
                else:
                    holdings[elem.tag] = ''
        return holdings


def get_availability(auth, num_to_search):
    r = requests.get(auth.url, headers=auth.get_header('GET'))
    return Availability(r.content)
