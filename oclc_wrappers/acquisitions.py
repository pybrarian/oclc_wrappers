import json

from .oclc_exceptions import RequestError
from .requestor import PORequest, ItemRequest, FundRequest
from .constants import PO_TEMPLATE, ITEM_TEMPLATE, ITEM_FUND_FIELDS
from .jsondict import JSONDict


class PurchaseOrder(JSONDict):
    """
    Represent a purchase order like a dict
    """

    def __init__(self, auth, *args, **kwargs):
        """
        Load the object with a template to allow easily accessing or setting
        items without having to initialize them. Then update with whatever
        args are passed in.

        :param auth: Authorization object implementing HMAC protocol
        :param args: Positional arguments
        :param kwargs: Keyword arguments, key=item pairs to add to dict
        """
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
        return get_all_purchase_order_items(self.auth,
                                            self['purchaseOrderNumber'])

    def create_in_wms(self):
        """
        Send and create this purchase order in WMS, clear the current values
        and replace with the values from WMS's response
        """
        r = send_purchase_order(self.auth, self)
        self.clear()
        self.update(json.loads(r.content))


class Item(JSONDict):
    """
    Represent a purchase order item as a Python object.

    The default behavior for most methods is 1 copy being bought using 1
    fund (thus there are multiple convenience properties for accessing the
    first instance of something, even though lots of getters and setters
    feels rather un-Pythonic).

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
    """

    def __init__(self, auth, *args, **kwargs):
        """
        :param auth: Authorization object implementing HMAC protocol
        :param args: Positional arguments
        :param kwargs: Keyword arguments, key=item pairs to add to dict
        """
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
        return ', '.join(self.worldcat['author'])

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

    def add_isbn(self, isbn):
        self.worldcat['isbn'].append(isbn)

    def add_note(self, note, note_type='STAFF', alert='NONE'):
        """
        Add a single note. All fields required or API will throw an error.

        :param note: The text of the note you want to add
        :param note_type: The type of note, see WMS for appropriate values
        :param alert: The type of alert, see WMS
        """
        self['notes']['note'].append({'content': note,
                                      'type': note_type,
                                      'alert': alert})

    def add_notes(self, *args, **kwargs):
        """
        Add multiple notes.
        :param args: The notes to append
        :param kwargs: Allows for note_type=value or alert=value, see add_note
        """
        for note in args:
            if note:
                self.add_note(note, **kwargs)

    def add_fund(self, copy=None, **kwargs):
        """
        Add a new fund item.
        :param copy: Copy number of item, if None defaults to first copy
        :param kwargs: The fund fields to update at key=value pairs
        :return: The index of the new fund for easy access
        """
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['booking'].append(self._new_fund(**kwargs))
        return len(self.copies[copy_index]['booking']) - 1

    def update_fund(self, copy_code=None, fund_code=None, **kwargs):
        """
        Update the information in a fund.
        :param copy_code: Copy code fund is in, will default to first if None
        :param fund_code: Fund code to update, will default to first if None
        :param kwargs: The fields of fund information to update as key=value
        """
        copy_index = self._get_copy_index(copy_code)
        copy_code = self.copies[copy_index]['copyConfigNumber']
        fund_index = self._get_fund_index(fund_code, copy_code)
        for key, val in kwargs.items():
            self._check_key(key)
            self.copies[copy_index]['booking'][fund_index][key] = val

    def fund_index_by_code(self, code, copy=None):
        """
        Get the index of a fund by the code of the fund.

        :param code: Code to search
        :param copy: Copy to search in, defaults to first if None
        :return: The index of the given fund
        :raises KeyError: if the fund is not found by the code
        """
        copy_index = self._get_copy_index(copy)
        for index, fund in enumerate(self.copies[copy_index]['booking']):
            if fund['budgetAccountCode'] == code:
                return index
        raise KeyError('{0} fund is not found.'.format(code))

    def copy_index_by_number(self, number=None):
        """
        Get the index of an item copy by its copy number
        :param number: The copy number
        :return: The index of given copy
        :raises KeyError: if the copy is not found
        """
        for index, copy in enumerate(self.copies):
            if copy['copyConfigNumber'] == number:
                return index
        raise KeyError

    def add_copy(self, **kwargs):
        """
        Add a copy of an item.
        :param kwargs: The fields to fill for the new copy
        :return: The index of the copy for ease of access
        """
        self['copyConfigs']['copyConfig'].append(self._new_copy(**kwargs))
        return len(self.copies) - 1

    def all_copies_same_branch(self, branch_id):
        """
        Set all copies of an item to the same branch location.
        :param branch_id: The ID of the branch
        """
        for copy in self.copies:
            copy['branchId'] = branch_id

    def set_branch(self, branch_id, copy=None):
        """
        Set the branch of an individual copy.

        :param branch_id: Id of the branch
        :param copy: Copy number to update, defaults to first if None
        """
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['branchId'] = branch_id

    def set_shelving(self, shelving_code, copy=None):
        """
        Set the branch of an individual copy.

        :param shelving_code: Code to be set
        :param copy: Copy number to update, defaults to first if None
        """
        copy_index = self._get_copy_index(copy)
        self.copies[copy_index]['shelvingLocationId'] = shelving_code

    def attach_to_order(self, order):
        """
        Attach the current item to a specified order in WMS.
        Then clear the current item and replace data with data returned from WMS.

        :param order: Purchase order number of the order to attach to.
        """
        new_item = attach_item_to_order(self.auth, order, self)
        self.clear()
        self.update(new_item)

    def _get_fund_index(self, fund, copy):
        """
        Get the index of a fund, useful for updating specific funds when there
        are more than one.
        :param fund: Fund code to update
        :param copy: Copy fund is for
        :return: 0 if no fund is specified (allows convenient access to first,
            which is the assumed default of most cases), else it searches for
            the fund code.
        :raises KeyError: Can implicitly raise a KeyError from
            self.fund_index_by_code if fund is specified but not found
        """
        if fund is None:
            return 0
        else:
            return self.fund_index_by_code(fund, copy=copy)

    def _get_copy_index(self, copy):
        """
        See above, but for copies.
        :param copy: Copy number to get index of.
        """
        if copy is None:
            return 0
        else:
            return self.copy_index_by_number(copy)

    def _new_fund(self, **kwargs):
        """
        Generate a new fund from the template to be inserted into the item.
        :param kwargs: The fund information to fill in as key=value
        :return: A filled-out fund item to be inserted
        """
        fund = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0]['booking'][
            0].copy()
        for key, val in kwargs.items():
            fund[key] = val
        return fund

    def _new_copy(self, **kwargs):
        """See above, but for copies"""
        copy = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0].copy()
        for key, val in kwargs.items():
            copy[key] = val
        return copy

    # TODO: Make this work on the __getitem__ __setitem__ level
    def _check_key(self, key):
        """
        Check to verify that the given keys are in the dict and therefore
        acceptable. Currently only for fund information.

        :param key: The key being updated.
        :raises KeyError: If the field is not recognized from the template
        """
        if key not in ITEM_FUND_FIELDS:
            raise KeyError


class Budget(JSONDict):
    def __init__(self, *args, **kwargs):
        super(Budget, self).__init__(*args, **kwargs)


class Fund(JSONDict):
    """Represent a WMS Fund"""

    def __init__(self, auth, *args, **kwargs):
        """
        Funds are read only; update with information from WMS API.
        Class is primarily convenience methods for accessing specific fund
        properties, namely amounts allocated, expended, encumbered, and
        remaining.
        :param auth:
        :param args:
        :param kwargs:
        """
        super(Fund, self).__init__(*args, **kwargs)
        self.auth = auth

    @property
    def allocation(self):
        return self._get_amount('amountBudgeted')

    @property
    def expended(self):
        return self._get_amount('amountExpended')

    @property
    def encumbered(self):
        return self._get_amount('amountEncumbered')

    @property
    def remaining(self):
        return self._get_amount('amountRemaining')

    @property
    def name(self):
        return self['name']

    @property
    def code(self):
        return self['code']

    @property
    def id(self):
        return self['allocation']['allocation']['id']

    def _get_amount(self, price_type):
        return self['allocation']['allocation'][price_type]['priceSpecification']['price']


def get_purchase_order(auth, po_number):
    """
    Request a purchase order from WMS Acquisitions API

    :param auth: Authorization object implementing HMAC protocol
    :param po_number: Number of the PO to be retrieved
    :return: a PurchaseOrder object with the data retrieved
    """
    requestor = PORequest(auth, 'read', po_number=po_number)
    r = requestor.send_request()
    check_status_code(r, (200,))
    return PurchaseOrder(auth, json.loads(r.content))


def get_all_purchase_order_items(auth, po_number):
    """
    Get all the items attached to a purchase order

    :param auth: Authorization object implementing HMAC protocol
    :param po_number: Number of the PO to retrieve items for
    :return: A list of Item objects attached to the specified purchase order
    """
    requestor = ItemRequest(auth, 'list', po_number=po_number)
    items = get_all_records(requestor)
    return [Item(auth, item) for item in items]


def create_purchase_order(auth, name, vendor_id, **kwargs):
    """
    Create a purchase order in WMS

    :param auth: Authorization object implementing HMAC protocol
    :param name: What to call your purchase order (required by WMS)
    :param vendor_id: ID of vendor for purchase order
    :param kwargs: Any other fields you wish to populate (see API docs)
    :return: a PurchaseOrder object with information provided plus WMS
        generated information such as a purchase order number and timestamps
    """
    po = PurchaseOrder(auth)
    po.name = name
    po.vendor_id = vendor_id
    if kwargs:
        for key, val in kwargs.items():
            po[key] = val
    po.create_in_wms()
    return po


def send_purchase_order(auth, po):
    """
    Send the purchase order information to WMS

    :param auth: Authorization object implementing HMAC protocol
    :param po: The PurchaseOrder object to send
    :return: The Response object from the API call
    """
    requestor = PORequest(auth, 'create', data=po)
    r = requestor.send_request()
    check_status_code(r, (201,))
    return r


def attach_item_to_order(auth, order, item):
    """
    Send an Item object to WMS attached to a purchase order
    :param auth: Authorization object implementing HMAC protocol
    :param order: The number of the purchase order to attach to
    :param item: The Item object to send
    :return: An Item object with the given information plus WMS generated
        data such
    """
    requestor = ItemRequest(auth=auth, action='create', po_number=order,
                            data=item)
    r = requestor.send_request()
    check_status_code(r, (201,), item)
    return Item(auth, json.loads(r.content))


def get_fund(auth, inst_id, fund, budget=None):
    """
    Get fund information from WMS

    If no budget is specified, you must use a fund's ID rather than it's code

    :param auth: Authorization object implementing HMAC protocol
    :param inst_id: Your institution's numeric Worldcat ID (not institutional
        identifier, i.e. not WEX for Westfield State University)
    :param fund: Code or ID of fund to get
    :param budget: Budget fund is part of
    :return: A Fund object with data from WMS
    """
    action = 'read'
    if budget is not None:
        action = 'by_fund_number'
    requestor = FundRequest(auth, action, inst_id, fund=fund, budget=budget)
    r = requestor.send_request()
    check_status_code(r, (200,))
    return Fund(auth, json.loads(r.content))


def search_funds(auth, inst_id, budget=None, parent=None):
    """
    Do a search for funds in a budget or with certain parent funds

    :param auth: Authorization object implementing HMAC protocol
    :param inst_id: Your institution's numeric Worldcat ID (not institutional
        identifier, i.e. not WEX for Westfield State University)
    :param budget: Budget period to search
    :param parent: Parent fund to search
    :return: A list of Fund objects populated with data from your search
    """
    query_params = _set_fund_query(budget, parent)
    requestor = FundRequest(auth, 'search', inst_id, params=query_params)
    funds = get_all_records(requestor)
    return [Fund(auth, fund) for fund in funds]


def _set_fund_query(budget, parent):
    """
    Get an appropriately formatted query dict to pass to the request
    :param budget: A budget period
    :param parent: A parent fund ID
    :return: A dict with the appropriate query parameters

    :raises KeyError if neither parameters is filled in, must have one to search
    """
    if budget is not None:
        return {'q': 'budgetPeriod:{budget}'.format(budget=budget)}
    elif parent is not None:
        return {'q': 'parentFundId:{parent}'.format(parent=parent)}
    else:
        raise KeyError


def get_all_records(requestor):
    """
    Helper function to coordinate fetching all records from an API

    :param requestor: A Requestor object with send_request and update_start_index
        and all_records_records_retrieved methods to be able to fetch multiple
        queries and coordinate when to stop
    :return: A list containing all the items as raw Python objects, should be
        fed to something to turn them into specialized objects (i.e. Items)
    """
    requestor.query_params.update({'startIndex': 1})
    all_items = []
    while True:
        r = requestor.send_request()
        check_status_code(r, (200,))
        elems = json.loads(r.content)
        all_items.extend(elems['entry'])
        requestor.update_start_index(10)
        if requestor.all_records_retrieved(int(elems['totalResults'])):
            break
    return all_items


def check_status_code(response, correct_codes, attempt=None):
    """
    Check the status code returned against the list of accepted status codes.
    If they match do nothing, else blow up.
    :param response: The raw Response object from a request, must implement
        status_code and content properties
    :param correct_codes: An iterable of acceptable status codes to return
    :param attempt: Optional URL of the attempted query
    :return: None

    :raises RequestError: if status codes do not match with anything in
        correct_codes iterable
    """
    if response.status_code not in correct_codes:
        raise RequestError(response.content, attempt=attempt)
