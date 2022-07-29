class SetFunction(dict):
	def __init__(self, *args, **kw):
		super(SetFunction, self).__init__(*args, **kw)
		self.domain = set(super(SetFunction, self).keys())
		self.image = set(super(SetFunction, self).values())

	def __setitem__(self, key, value):
		super(SetFunction, self).__setitem__(key, value)
		self.domain.add(key)
		self.image = set(super(SetFunction, self).values())

	def __delitem__(self, key):
		super(SetFunction, self).__delitem__(key)
		self.domain = set(super(SetFunction, self).keys())
		self.image = set(super(SetFunction, self).values())

	def mapsto(self, codomain):
		return self.image.issubset(codomain)

	def imageof(self, A):
		return set(v for k,v in self.items() if k in A)

	def preimage(self, y):
		return set(k for k,v in self.items() if v == y)

	def restriction(self, A):
		return SetFunction({k:v for k,v in self.items() if k in A})

	# Return the composite f circ g
	@staticmethod
	def compose(f, g):
		if not g.mapsto(f.domain):
			raise Exception('Tried composing two incomposible functions')

		composite = {}
		for x,y in g.items():
			composite[x] = f[y]

		return SetFunction(composite)