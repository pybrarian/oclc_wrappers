import os
import unittest

from httmock import HTTMock, urlmatch

from oclc_wrappers.availability import get_availability
from oclc_wrappers.auth import Auth
from oclc_wrappers.tests.configTest import config_object


@urlmatch(netloc=r'(.*\.)?worldcat\.org$')
def oclc_mock(url, request):
    path = os.path.join(os.path.dirname(__file__), 'availabilityCall.xml')
    with open(path, 'rb') as data:
        return data.read()


class TestAvailability(unittest.TestCase):

    def setUp(self):
        with HTTMock(oclc_mock):
            self.avail = get_availability(Auth(config_object), 12345)

    def test_has_holdings(self):
        self.assertTrue(self.avail.has_holdings)

    def test_holdings_are_correctly_set(self):
        # The item id is about the weirdest, furthest-down bit of info
        # That seemed good reason to make it the test case
        item_id = int(self.avail.holdings[0].holding['circulations']['circulation']['itemId'])
        self.assertEqual(item_id, 30386000085578)


if __name__ == '__main__':
    unittest.main()
