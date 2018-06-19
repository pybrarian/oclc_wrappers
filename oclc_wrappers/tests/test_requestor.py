import os
import unittest

from httmock import HTTMock, urlmatch

from oclc_wrappers.auth import Auth
from oclc_wrappers.tests.configTest import config_object

# TODO: Implement
@urlmatch(netloc=r'(.*\.)?worldcat\.org$')
def oclc_mock(url, request):
    path = os.path.join(os.path.dirname(__file__), 'availabilityCall.xml')
    with open(path, 'rb') as data:
        return data.read()

if __name__ == '__main__':
    unittest.main()
