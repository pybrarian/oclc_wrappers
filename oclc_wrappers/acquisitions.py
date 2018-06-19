import json

from oclc_wrappers.oclc_exceptions import RequestError
from oclc_wrappers.requestor import HMACRequest
from oclc_wrappers.constants import (PO_TEMPLATE, ITEM_TEMPLATE, ITEM_FUND_FIELDS, PO_URLS,
                       ITEM_URLS, FUND_URLS)
from oclc_wrappers.jsondict import JSONDict


class PurchaseOrder(JSONDict):

    def __init__(self, auth, *args, **kwargs):
        self.update(PO_TEMPLATE)
        super(PurchaseOrder, self).__init__(*args, **kwargs)
        self.auth = auth

    @property
    def vendor_id(self):
        return self['vendor']['vendorId']

    @vendor_id.setter
    def vendor_id(self, val):
        self['vendor']['vendorId'] = val

    @property
    def vendor_local_id(self):
        return self['vendor']['localIdentifier']

    @vendor_local_id.setter
    def vendor_local_id(self, val):
        self['vendor']['localIdentifier'] = val

    @property
    def name(self):
        return self['orderName']

    @name.setter
    def name(self, val):
        self['orderName'] = val

    @property
    def number(self):
        return self['purchaseOrderNumber']

    @property
    def po_items(self):
        return get_all_purchase_order_items(self.auth, self['purchaseOrderNumber'])

    def create_in_wms(self):
        r = send_purchase_order(self.auth, self)
        self.clear()
        self.update(json.loads(r.content))


class Item(JSONDict):
    """
    Represent a purchase order item as a Python object.

    The default behavior for most methods is 1 copy being bought using 1
    fund (there are also several convenience properties for accessing the
    first instance of something).

    The following fields are more or less required of an item to be able to
    send it to WMS:
    Resource:
        self.oclc_number = self['resource']['worldcatResource']['oclcNumber']
    Fund:
        self.first_vendor_id = self['copyConfigs']['copyConfig'][0]['booking'][0]['vendorId']
        self.first_percentage = self['copyConfigs']['copyConfig'][0]['booking'][0]['percentage']
    Branch:
        self.first_copy_branch = self['copyConfigs']['copyConfig'][0]['branchId']
    Shelving location:
        self.first_copy_shelving = self['copyConfigs']['copyConfig'][0]['shelvingLocationId']
    Order type:
        self.order_type = self['orderType']
    Price:
        self.price = self['orderingPrice']

    :arg auth - An Auth object that implements HMAC authentication
    """

    def __init__(self, auth, *args, **kwargs):
        self.update(ITEM_TEMPLATE)
        super(Item, self).__init__(*args, **kwargs)
        self.auth = auth

    @property
    def copies(self):
        return self['copyConfigs']['copyConfig']

    @property
    def first_copy(self):
        return self.copies[0]

    @property
    def first_fund(self):
        return self.first_copy['booking'][0]

    @property
    def first_fund_code(self):
        return self.first_fund['budgetAccountCode']

    @first_fund_code.setter
    def first_fund_code(self, val):
        self.first_fund['budgetAccountCode'] = val

    @property
    def first_percentage(self):
        return self.first_fund['percentage']

    @first_percentage.setter
    def first_percentage(self, val):
        self.first_fund['percentage'] = val

    @property
    def first_copy_branch(self):
        return self.first_copy['branchId']

    @first_copy_branch.setter
    def first_copy_branch(self, val):
        self.first_copy['branchId'] = val

    @property
    def first_copy_shelving(self):
        return self.first_copy['shelvingLocationId']

    @first_copy_shelving.setter
    def first_copy_shelving(self, val):
        self.first_copy['shelvingLocationId'] = val

    @property
    def order_type(self):
        return self['orderType']

    @order_type.setter
    def order_type(self, val):
        self['orderType'] = val

    @property
    def worldcat(self):
        return self['resource']['worldcatResource']

    @property
    def oclc_number(self):
        return self.worldcat['oclcNumber']

    @oclc_number.setter
    def oclc_number(self, val):
        self.worldcat['oclcNumber'] = val

    @property
    def price(self):
        return self['orderingPrice']

    @price.setter
    def price(self, val):
        self['orderingPrice'] = val

    @property
    def title(self):
        return self.worldcat['title']

    @property
    def author(self):
        return ', '.join(x for x in self.worldcat['author'])

    @property
    def vendor_item_number(self):
        return self['vendorOrderItemNumber']

    @vendor_item_number.setter
    def vendor_item_number(self, val):
        self['vendorOrderItemNumber'] = val

    @property
    def notes(self):
        return ', '.join([x['content'] for x in self['notes']['note']])

    @property
    def has_multiple_copies(self):
        return len(self.copies) > 1

    def attach_to_order(self, order):
        new_item = attach_item_to_order(self.auth, order, self)
        self.clear()
        self.update(new_item)

    def add_isbn(self, isbn):
        self.worldcat['isbn'].append(isbn)

    def add_note(self, note):
        self['notes']['note'].append({'content': note, 'type': 'STAFF', 'alert': 'NONE'})

    def add_notes(self, *args):
        self['notes']['note'] = [{'content': note, 'type': 'STAFF', 'alert': 'NONE'}
                                 for note in args if note]

    def add_fund(self, copy=None, **kwargs):
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['booking'].append(self._new_fund(**kwargs))
        return len(self.copies[copy_index]['booking']) - 1

    def update_fund(self, copy_code=None, fund_code=None, **kwargs):
        copy_index = self._get_copy_index(copy_code)
        copy_code = self.copies[copy_index]['copyConfigNumber']
        fund_index = self._get_fund_index(fund_code, copy_code)
        for key, val in kwargs.items():
            self._check_key(key)
            self.copies[copy_index]['booking'][fund_index][key] = val

    def fund_index_by_code(self, code, copy=None):
        copy_index = self._get_copy_index(copy)
        for index, fund in enumerate(self.copies[copy_index]['booking']):
            if fund['budgetAccountCode'] == code:
                return index
        raise KeyError

    def copy_index_by_number(self, number=None):
        for index, copy in enumerate(self.copies):
            if copy['copyConfigNumber'] == number:
                return index
        raise KeyError

    def add_copy(self, **kwargs):
        self['copyConfigs']['copyConfig'].append(self._new_copy(**kwargs))
        return len(self.copies) - 1

    def all_copies_same_branch(self, branch_id):
        for copy in self.copies:
            copy['branchId'] = branch_id

    def set_branch(self, branch_id, copy=None):
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['branchId'] = branch_id

    def set_shelving(self, shelving_code, copy=None):
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['shelvingLocationId'] = shelving_code

    def _get_fund_index(self, fund, copy):
        if fund is None:
            return 0
        else:
            return self.fund_index_by_code(fund, copy=copy)

    def _get_copy_index(self, copy):
        if copy is None:
            return 0
        else:
            return self.copy_index_by_number(copy)

    def _new_fund(self, **kwargs):
        fund = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0]['booking'][0].copy()
        for key, val in kwargs.items():
            fund[key] = val
        return fund

    def _new_copy(self, **kwargs):
        copy = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0].copy()
        for key, val in kwargs.items():
            copy[key] = val
        return copy

    def _check_key(self, key):
        if key not in ITEM_FUND_FIELDS:
            raise KeyError


class Budget(JSONDict):

    def __init__(self, *args, **kwargs):
        super(Budget, self).__init__(*args, **kwargs)


class Fund(JSONDict):

    def __init__(self, auth, *args, **kwargs):
        super(Fund, self).__init__(*args, **kwargs)
        self.auth = auth

    @property
    def allocation(self):
        return self._get_price('amountBudgeted')

    @property
    def expended(self):
        return self._get_price('amountExpended')

    @property
    def encumbered(self):
        return self._get_price('amountEncumbered')

    @property
    def remaining(self):
        return self._get_price('amountRemaining')

    @property
    def name(self):
        return self['name']

    @property
    def code(self):
        return self['code']

    @property
    def id(self):
        return self['allocation']['allocation']['id']

    def _get_price(self, price_type):
        return self['allocation']['allocation'][price_type]['priceSpecification']['price']


def po_request(auth):
    return HMACRequest(auth, PO_URLS)


def item_request(auth):
    return HMACRequest(auth, ITEM_URLS)


def fund_request(auth):
    return HMACRequest(auth, FUND_URLS)


def get_purchase_order(auth, po_number):
    requestor = po_request(auth)
    url_params = {'order': po_number}
    r = requestor.send_request('read', url_params=url_params)
    check_status_code(r, (200,))
    return PurchaseOrder(auth, json.loads(r.content))


def get_all_purchase_order_items(auth, po_number):
    requestor = item_request(auth)
    url_params = {'order': po_number}
    items = get_all_records(requestor, 'list', url_params=url_params)
    return [Item(auth, item) for item in items]


def create_purchase_order(auth, name, vendor_id, **kwargs):
    po = PurchaseOrder(auth)
    po.name = name
    po.vendor_id = vendor_id
    if kwargs:
        for key, val in kwargs.items():
            po[key] = val
    po.create_in_wms()
    return po


def send_purchase_order(auth, po):
    requestor = po_request(auth)
    r = requestor.send_request('create', data=po)
    check_status_code(r, (201,))
    return r


# TODO: Implement
def update_purchase_order(auth, po_number):
    pass


def attach_item_to_order(auth, order, item):
    requestor = item_request(auth=auth)
    url_params = {'order': order}
    r = requestor.send_request('create', url_params=url_params)
    check_status_code(r, (201,), item)
    return Item(auth, json.loads(r.content))


def get_fund(auth, inst_id, fund, budget=None):
    action = 'read'
    if budget is not None:
        action = 'by_fund_number'
    requestor = fund_request(auth)
    url_params = {'inst_id': inst_id, 'fund': fund, 'budget': budget}
    r = requestor.send_request(action, url_params=url_params)
    check_status_code(r, (200,))
    return Fund(auth, json.loads(r.content))


def search_funds(auth, inst_id, budget=None, parent=None):
    requestor = fund_request(auth)
    query_params = _set_fund_query(budget, parent)
    url_params = {'inst_id': inst_id}
    funds = get_all_records(requestor, 'search', url_params=url_params, query_params=query_params)
    return [Fund(auth, fund) for fund in funds]


def _set_fund_query(budget, parent):
    if budget is not None:
        return {'q': 'budgetPeriod:{budget}'.format(budget=budget)}
    elif parent is not None:
        return {'q': 'parentFundId:{parent}'.format(parent=parent)}
    else:
        raise KeyError


def all_records_retrieved(total_records, starting_index):
    return total_records < starting_index


def get_all_records(requestor, action, url_params=None, query_params=None):
    if query_params is None:
        query_params = {}
    query_params.update({'startIndex': 1})
    all_items = []
    while True:
        r = requestor.send_request(action, url_params=url_params, query_params=query_params)
        check_status_code(r, (200,))
        elems = json.loads(r.content)
        all_items.extend(elems['entry'])
        query_params['startIndex'] += 10
        if all_records_retrieved(int(elems['totalResults']), query_params['startIndex']):
            break
    return all_items


def check_status_code(request, correct_codes, attempt=None):
    if request.status_code not in correct_codes:
        raise RequestError(request.content, attempt=attempt)
