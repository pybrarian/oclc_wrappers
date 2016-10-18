class JSONDict(dict):

    def __init__(self, *args, **kwargs):
        super(JSONDict, self).__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        if key in self:
            dict.__setitem__(self, key, value)
        else:
            raise KeyError
