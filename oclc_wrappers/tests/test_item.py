import unittest

from oclc_wrappers.acquisitions import Item
from oclc_wrappers.tests.configTest import config_object


class TestItem(unittest.TestCase):

    def test_adding_a_generic_fund(self):
        item = Item(config_object)
        item.add_fund()
        self.assertEqual(2, len(item.copies[0]['booking']))

if __name__ == '__main__':
    unittest.main()
