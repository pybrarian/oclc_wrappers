import os
from unittest import TestCase

from oclc_wrappers.worldcat import WorldcatResource, WorldcatHoldings


class TestWorldcatResource(TestCase):

    def setUp(self):
        filepath = os.path.join(os.path.dirname(__file__), 'resourceXml.xml')
        with open(filepath, 'rb') as f:
            self.record = WorldcatResource('1234key', f.read())

    def test_oclc_number(self):
        self.assertEqual('320842055', self.record.oclc_number)

    def test_cataloging_language(self):
        self.assertEqual('eng', self.record.cataloging_language)

    def test_control_field(self):
        self.assertEqual('090512s2009    enkafg  ob    001 0deng d',
                         self.record.control_field_008)

    def test_publisher(self):
        self.assertEqual('Oxford University Press', self.record.publisher)

    def test_publication_date(self):
        self.assertEqual('2009', self.record.publication_date)

    def test_title(self):
        self.assertEqual('Beethoven', self.record.title)

    def test_authors(self):
        self.assertEqual('William Kinderman', self.record.authors)


class TestWorldcatHoldings(TestCase):

    def setUp(self):
        has_holdings = os.path.join(os.path.dirname(__file__), 'worldcatholdings.xml')
        with open(has_holdings, 'rb') as f:
            self.holdings = WorldcatHoldings(f.read())

        no_holdings = os.path.join(os.path.dirname(__file__), 'noworldcatholdings.xml')
        with open(no_holdings, 'rb') as f:
            self.no_holdings = WorldcatHoldings(f.read())

    def test_has_holdings(self):
        self.assertTrue(self.holdings.has_holdings)

    def test_no_holdings(self):
        self.assertFalse(self.no_holdings.has_holdings)
