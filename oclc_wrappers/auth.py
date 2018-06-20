from authliboclc import user, wskey


class Auth:

    def __init__(self, params, options=None):
        self.key = params.get('key')
        self.secret = params.get('secret')
        self.principleId = params.get('principleId')
        self.principleIDNS = params.get('principleIDNS')
        self.institutionId = params.get('institutionId')
        self.options = options
        self.etag = None

        self.user = user.User(
            authenticating_institution_id=self.institutionId,
            principal_id=self.principleId,
            principal_idns=self.principleIDNS)

        self.wsKey = wskey.Wskey(
            key=self.key,
            secret=self.secret,
            options=self.options)

    def get_signature(self, http_verb, url):
        return self.wsKey.get_hmac_signature(method=http_verb,
                                             request_url=url,
                                             options={'user': self.user,
                                                      'authParams': None})

    def get_header(self, http_verb, url):
        headers = {'Authorization': self.get_signature(http_verb, url),
                   'Accept': 'application/json'}
        if self.etag and http_verb == 'PUT':
            headers.update({'If-Match': self.etag})
        if http_verb == 'POST' or http_verb == 'PUT':
            headers.update({'Content-Type': 'application/json'})
        return headers

    def set_etag(self, request):
        try:
            self.etag = request.headers['ETag']
        except KeyError:
            pass
