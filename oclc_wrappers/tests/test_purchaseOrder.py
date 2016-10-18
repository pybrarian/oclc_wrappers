import unittest

from httmock import HTTMock, urlmatch

from oclc_wrappers.acquisitions import PurchaseOrder
from oclc_wrappers.tests.configTest import config_object


class TestPurchaseOrder(unittest.TestCase):

    def test_adding_a_vendor_id(self):
        blank_po = PurchaseOrder(config_object)
        blank_po['vendor']['vendorId'] = '12345'
        self.assertEqual('12345', blank_po['vendor']['vendorId'])

    def test_that_existence_check_works(self):
        blank_po = PurchaseOrder(config_object)
        blank_po['orderName'] = 'superCool'


if __name__ == '__main__':
    unittest.main()
