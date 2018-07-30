import copy

from .oclc_exceptions import RequestError
from .requestor import HMACRequest
from .constants import PO_TEMPLATE, ITEM_TEMPLATE, ITEM_FUND_FIELDS, PO_URLS, ITEM_URLS, FUND_URLS


class PurchaseOrder(object):

    def __init__(self, auth, *args, **kwargs):
        self._data = copy.deepcopy(PO_TEMPLATE)
        self._data.update(*args, **kwargs)
        self.auth = auth

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    @property
    def vendor_id(self):
        return self._data['vendor']['vendorId']

    @vendor_id.setter
    def vendor_id(self, val):
        self._data['vendor']['vendorId'] = val

    @property
    def vendor_local_id(self):
        return self._data['vendor']['localIdentifier']

    @vendor_local_id.setter
    def vendor_local_id(self, val):
        self._data['vendor']['localIdentifier'] = val

    @property
    def name(self):
        return self._data['orderName']

    @name.setter
    def name(self, val):
        self._data['orderName'] = val

    @property
    def number(self):
        return self._data['purchaseOrderNumber']

    @property
    def po_items(self):
        return get_all_purchase_order_items(self.auth, self._data['purchaseOrderNumber'])

    def create_in_wms(self):
        r = send_purchase_order(self.auth, self._data)
        self._data.clear()
        self._data.update(r.json())


class Item(object):
    """
    Represent a purchase order item as a Python object.

    The default behavior for most methods is 1 copy being bought using 1
    fund (there are also several convenience properties for accessing the
    first instance of something).

    The following fields are more or less required of an item to be able to
    send it to WMS:
    Resource:
        self.oclc_number = self._data['resource']['worldcatResource']['oclcNumber']
    Fund:
        self.first_vendor_id = self._data['copyConfigs']['copyConfig'][0]['booking'][0]['vendorId']
        self.first_percentage = self._data['copyConfigs']['copyConfig'][0]['booking'][0]['percentage']
    Branch:
        self.first_copy_branch = self._data['copyConfigs']['copyConfig'][0]['branchId']
    Shelving location:
        self.first_copy_shelving = self._data['copyConfigs']['copyConfig'][0]['shelvingLocationId']
    Order type:
        self.order_type = self._data['orderType']
    Price:
        self.price = self._data['orderingPrice']

    :arg auth - An Auth object that implements HMAC authentication
    """

    def __init__(self, auth, *args, **kwargs):
        self._data = copy.deepcopy(ITEM_TEMPLATE)
        self._data.update(*args, **kwargs)
        self.auth = auth

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    @property
    def copies(self):
        return self._data['copyConfigs']['copyConfig']

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
        return self._data['orderType']

    @order_type.setter
    def order_type(self, val):
        self._data['orderType'] = val

    @property
    def worldcat(self):
        return self._data['resource']['worldcatResource']

    @property
    def oclc_number(self):
        return self.worldcat['oclcNumber']

    @oclc_number.setter
    def oclc_number(self, val):
        self.worldcat['oclcNumber'] = val

    @property
    def price(self):
        return self._data['orderingPrice']

    @price.setter
    def price(self, val):
        self._data['orderingPrice'] = val

    @property
    def title(self):
        return self.worldcat['title']

    @property
    def author(self):
        return ', '.join(x for x in self.worldcat['author'])

    @property
    def vendor_item_number(self):
        return self._data['vendorOrderItemNumber']

    @vendor_item_number.setter
    def vendor_item_number(self, val):
        self._data['vendorOrderItemNumber'] = val

    @property
    def notes(self):
        return ', '.join([x['content'] for x in self._data['notes']['note']])

    @property
    def has_multiple_copies(self):
        return len(self.copies) > 1

    def attach_to_order(self, order):
        new_item = attach_item_to_order(self.auth, order, self._data)
        self._data.clear()
        self._data.update(new_item._data)

    def add_isbn(self, isbn):
        self.worldcat['isbn'].append(isbn)

    def add_note(self, note):
        self._data['notes']['note'].append({'content': note, 'type': 'STAFF', 'alert': 'NONE'})

    def add_notes(self, *args):
        self._data['notes']['note'] = [{'content': note, 'type': 'STAFF', 'alert': 'NONE'}
                                       for note in args if note]

    def add_fund(self, copy_data=None, **kwargs):
        copy_index = self._get_copy_index(copy_data)
        self.copies[copy_index]['booking'].append(self._new_fund(**kwargs))
        return len(self.copies[copy_index]['booking']) - 1

    def update_fund(self, copy_code=None, fund_code=None, **kwargs):
        copy_index = self._get_copy_index(copy_code)
        copy_code = self.copies[copy_index]['copyConfigNumber']
        fund_index = self._get_fund_index(fund_code, copy_code)
        for key, val in kwargs.items():
            self._check_key(key)
            self.copies[copy_index]['booking'][fund_index][key] = val

    def fund_index_by_code(self, code, copy_data=None):
        copy_index = self._get_copy_index(copy_data)
        for index, fund in enumerate(self.copies[copy_index]['booking']):
            if fund['budgetAccountCode'] == code:
                return index
        raise KeyError

    def copy_index_by_number(self, number=None):
        for index, copy_data in enumerate(self.copies):
            if copy_data['copyConfigNumber'] == number:
                return index
        raise KeyError

    def add_copy(self, **kwargs):
        self._data['copyConfigs']['copyConfig'].append(self._new_copy(**kwargs))
        return len(self.copies) - 1

    def all_copies_same_branch(self, branch_id):
        for copy_data in self.copies:
            copy_data['branchId'] = branch_id

    def set_branch(self, branch_id, copy_data=None):
        copy_index = self._get_copy_index(copy_data)
        self.copies[copy_index]['branchId'] = branch_id

    def set_shelving(self, shelving_code, copy_data=None):
        copy_index = self._get_copy_index(copy_data)
        self.copies[copy_index]['shelvingLocationId'] = shelving_code

    def _get_fund_index(self, fund, copy_data):
        if fund is None:
            return 0
        else:
            return self.fund_index_by_code(fund, copy_data=copy_data)

    def _get_copy_index(self, copy_data):
        if copy_data is None:
            return 0
        else:
            return self.copy_index_by_number(copy_data)

    def _new_fund(self, **kwargs):
        fund = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0]['booking'][0].copy()
        for key, val in kwargs.items():
            fund[key] = val
        return fund

    def _new_copy(self, **kwargs):
        new_copy = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0].copy()
        for key, val in kwargs.items():
            new_copy[key] = val
        return new_copy

    def _check_key(self, key):
        if key not in ITEM_FUND_FIELDS:
            raise KeyError


class Budget(object):

    def __init__(self, *args, **kwargs):
        self._data = dict(*args, **kwargs)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value


class Fund(object):

    def __init__(self, auth, *args, **kwargs):
        self._data = dict(*args, **kwargs)
        self.auth = auth

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

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
        return self._data['name']

    @property
    def code(self):
        return self._data['code']

    @property
    def id(self):
        return self._data['allocation']['allocation']['id']

    def _get_price(self, price_type):
        return self._data['allocation']['allocation'][price_type]['priceSpecification']['price']


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
    return PurchaseOrder(auth, r.json())


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
    check_status_code(r, (201,), po)
    return r


def delete_purchase_order(auth, order):
    requestor = po_request(auth)
    r = requestor.send_request('delete', url_params={'order': order})
    check_status_code(r, (200,))


# TODO: Implement
def update_purchase_order(auth, po_number):
    pass


def attach_item_to_order(auth, order, item):
    requestor = item_request(auth=auth)
    url_params = {'order': order}
    r = requestor.send_request('create', url_params=url_params, data=item)
    check_status_code(r, (201,), item)
    return Item(auth, r.json())


def get_fund(auth, inst_id, fund, budget=None):
    action = 'read'
    if budget is not None:
        action = 'by_fund_number'
    requestor = fund_request(auth)
    url_params = {'inst_id': inst_id, 'fund': fund, 'budget': budget}
    r = requestor.send_request(action, url_params=url_params)
    check_status_code(r, (200,))
    return Fund(auth, r.json())


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
        elems = r.json()
        all_items.extend(elems['entry'])
        query_params['startIndex'] += 10
        if all_records_retrieved(int(elems['totalResults']), query_params['startIndex']):
            break
    return all_items


def check_status_code(request, correct_codes, attempt=None):
    if request.status_code not in correct_codes:
        raise RequestError(request.content, attempt=attempt)
