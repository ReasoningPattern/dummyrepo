def pop_u16(self):
	"""
	Remove the last two elements in self.data and return
	"""
	self.data.pop()
	self.data.pop()
	return self.data