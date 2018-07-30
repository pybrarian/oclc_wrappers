import xml.etree.ElementTree as ET
from .constants import NS


class XMLObject(object):

    def __init__(self, root_name, data=None):
        try:
            self.root = ET.fromstring(data)
        except TypeError:
            self.root = ET.Element(self.add_namespace(root_name))

    def find_one(self, elem, node=None):
        try:
            return node.find(self._xpath(elem), NS)
        except AttributeError:
            return self.root.find(self._xpath(elem), NS)

    def find_all(self, elem, node=None):
        try:
            return node.findall(self._xpath(elem), NS)
        except AttributeError:
            return self.root.findall(self._xpath(elem), NS)

    def more_than_one(self, elem):
        return len(list(self.find_all(elem))) > 1

    def element_exists(self, elem, node=None):
        x = self.find_one(elem, node)
        if x is None:
            return False
        else:
            return True

    def add_namespace(self, elem):
        return '{ns}{el}'.format(ns='{'+self.ns(elem)+'}', el=elem)

    def get_or_make_elem(self, elem, parent):
        el = self.find_one(elem, parent)
        if el is None:
            return self.make_subelem(elem, parent)
        else:
            return el

    def make_subelem(self, elem, parent):
        return ET.SubElement(parent, self.add_namespace(elem))

    def get_by_elem(self, elem, parent, comparison):
        for el in parent:
            comp = self.find_one(elem, el)
            if comparison == comp:
                return el

    def convert_to_camel(self, name):
        if '_' in name:
            new_name = name.split('_')
            return new_name[0] + ''.join([x.title() for x in new_name[1:]])
        else:
            return name

    def _xpath(self, elem):
        return './/{ns_elem}'.format(ns_elem=self.add_namespace(elem))

    def ns(self, elem):
        raise NotImplementedError
