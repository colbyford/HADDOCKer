# A dictionary with default values for non-existing entries

import UserDict, copy

class DictWithDefault(UserDict.UserDict):

    def __init__(self, default):
	self.data = {}
	self.default = default

    def __getitem__(self, key):
	try:
	    item = self.data[key]
	except KeyError:
	    item = copy.copy(self.default)
	    self.data[key] = item
	return item

    def __delitem__(self, key):
	try:
	    del self.data[key]
	except KeyError:
	    pass
