import os
import unittest

from httmock import HTTMock, urlmatch

from oclc_wrappers.requestor import PORequest
from oclc_wrappers.auth import Auth
from oclc_wrappers.tests.configTest import config_object

@urlmatch(netloc=r'(.*\.)?worldcat\.org$')
def oclc_mock(url, request):
    path = os.path.join(os.path.dirname(__file__), 'availabilityCall.xml')
    with open(path, 'rb') as data:
        return data.read()


class TestPORequestor(unittest.TestCase):

    def setUp(self):
        self.po_req = PORequest(auth=Auth(config_object), action='read', po_number='PO-123-45')

    def test_send_request(self):
        with HTTMock(oclc_mock):
            r = self.po_req.send_request()
        self.assertEqual(r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
