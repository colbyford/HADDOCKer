# A more or less complete user-defined wrapper around string objects

class UserString:
	def __init__(self, string = None):
		self.data = []
		if string is not None:
			if type(string) == type(self.data):
				self.data[:] = string
			else:
				self.data[:] = string.data[:]
	def __repr__(self): return repr(self.data)
	def __cmp__(self, string):
		if type(string) == type(self.data):
			return cmp(self.data, string)
		else:
			return cmp(self.data, string.data)
	def __len__(self): return len(self.data)
	def __getitem__(self, i): return self.data[i]
	def __setitem__(self, i, item): self.data[i] = item
	def __delitem__(self, i): del self.data[i]
	def __getslice__(self, i, j):
		userstring = UserString()
		userstring.data[:] = self.data[i:j]
		return userstring
	def __setslice__(self, i, j, string):
		if type(string) == type(self.data):
			self.data[i:j] = string
		else:
			self.data[i:j] = string.data
	def __delslice__(self, i, j): del self.data[i:j]
	def __add__(self, string):
		if type(string) == type(self.data):
			return self.__class__(self.data + string)
		else:
			return self.__class__(self.data + string.data)
	def __radd__(self, string):
		if type(string) == type(self.data):
			return self.__class__(string + self.data)
		else:
			return self.__class__(string.data + self.data)
	def __mul__(self, n):
		return self.__class__(self.data*n)
	__rmul__ = __mul__
