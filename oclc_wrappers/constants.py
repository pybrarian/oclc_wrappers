from collections import namedtuple

UrlAndVerb = namedtuple('UrlAndVerb', 'url verb')

PO_URLS = {
    'create': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders', 'POST'),
    'read': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}', 'GET'),
    'update': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}', 'PUT'),
    'delete': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}', 'DELETE'),
    'submit': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/submissions', 'POST')
}

ITEM_URLS = {
    'create': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/items', 'POST'),
    'read': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/items/{item}', 'GET'),
    'update': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/items/{item}', 'PUT'),
    'delete': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/items/{item}', 'DELETE'),
    'list': UrlAndVerb('https://acq.sd00.worldcat.org/purchaseorders/{order}/items', 'GET')
}

WORLDCAT_RESOURCE_URLS = {
    'opensearch': UrlAndVerb('http://www.worldcat.org/webservices/catalog/search/opensearch', 'GET'),
    'sru': UrlAndVerb('http://www.worldcat.org/webservices/catalog/search/sru', 'GET'),
    'oclc_number': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/{number}', 'GET'),
    'isbn': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/isbn/{number}', 'GET'),
    'issn': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/issn/{number}', 'GET'),
    'standard_number': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/sn/{number}', 'GET'),
    'citation': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/citations/{number}', 'GET')
}

WORLDCAT_LIBRARY_URLS = {
    'oclc': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/libraries/{number}', 'GET'),
    'isbn': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/libraries/isbn/{number}', 'GET'),
    'issn': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/libraries/issn/{number}', 'GET'),
    'standard_number': UrlAndVerb('http://www.worldcat.org/webservices/catalog/content/libraries/sn/{number}', 'GET')
}

FUND_URLS = {
    'read': UrlAndVerb('https://{inst_id}.share.worldcat.org/acquisitions/fund/data/{fund}', 'GET'),
    'by_fund_number': UrlAndVerb('https://{inst_id}.share.worldcat.org/acquisitions/fund/data/{budget}-{fund}', 'GET'),
    'search': UrlAndVerb('https://{inst_id}.share.worldcat.org/acquisitions/fund/search', 'GET')
}

CLASSIFY_URL = {
    'read': UrlAndVerb('http://classify.oclc.org/classify2/Classify', 'GET')
}

ITEM_TEMPLATE = {
    'claimingSettings': None,
    'copyConfigs': {
        'copyConfig': [{
            'booking': [{
                'amount': None,
                'budgetAccountCode': None,
                'budgetAccountName': None,
                'percentage': None
            }],
            'branchId': None,
            'cancellationEndDate': None,
            'cancellationStartDate': None,
            'copyConfigNumber': None,
            'copyCount': None,
            'invoicedPercentage': None,
            'link': None,
            'orderStatus': None,
            'paidPercentage': None,
            'purchaseOrderItemNumber': None,
            'purchaseStatus': None,
            'shelvingLocationId': None
        }],
        'link': []
    },
    'discountPercentage': None,
    'insertTime': None,
    'lastUpdateTime': None,
    'link': None,
    'materialType': None,
    'orderItemNumber': None,
    'orderItemNumberRange': None,
    'orderType': 'FIRM_ORDER',
    'orderingPrice': None,
    'position': None,
    'preferredIdentifier': None,
    'preferredIdentifierType': None,
    'processingType': None,
    'quantity': None,
    'requester': None,
    'resource': {
        'kbwcCollectionResource': None,
        'kbwcEntryResource': None,
        'worldcatResource': {
            'author': [],
            'edition': None,
            'isbn': [],
            'issn': [],
            'materialType': None,
            'oclcNumber': None,
            'publisher': None,
            'title': None,
            'year': None
        }
    },
    'serviceCharge': None,
    'shippingAddressId': None,
    'shippingPrice': None,
    'shippingType': None,
    'sourceOfInformation': None,
    'subject': None,
    'notes': {'note': [], 'link': []},
    'tax1Percentage': None,
    'tax2Percentage': None,
    'totalPrice': None,
    'vendorOrderItemNumber': None
}

PO_TEMPLATE = {
    'action': None,
    'comment': None,
    'currency': None,
    'customerNumber': None,
    'exchangeRate': None,
    'insertTime': None,
    'lastUpdateTime': None,
    'link': {'href': None},
    'orderDate': None,
    'orderItemCount': None,
    'orderName': None,
    'orderNumberRange': None,
    'processing': None,
    'purchaseOrderItems': None,
    'purchaseOrderNumber': None,
    'purchaseOrderState': None,
    'shippingAddressId': None,
    'shippingType': None,
    'taxCalculationMethod': None,
    'totalOrderPrice': None,
    'vendor': {
        'vendorId': None,
        'vendorName': None,
        'localIdentifier': None
    },
    'vendorMessage': None,
    'vendorOrderNumber': None
}

ITEM_FUND_FIELDS = ITEM_TEMPLATE['copyConfigs']['copyConfig'][0]['booking'][0].keys()

NS = {
    'classify': 'http://classify.oclc.org',
    'wc_resource': 'http://www.loc.gov/MARC21/slim'
}