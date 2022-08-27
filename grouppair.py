from train_track import *
from whitehead import *

class GroupPair:
	def __init__(self, F, ws):
		self.F = F
		self.ws = [ConjCyclicSubgroup(w) for w in ws]

		self.F_canonical = FreeGroup(F.rank())
		phi = FreeGroupMorphism('')
		phi._domain = self.F
		phi._codomain = self.F_canonical
		data = {}
		for x, y in zip(self.F.gens(), self.F_canonical.gens()):
			data[x] = y
			data[x.inverse()] = y.inverse()
		phi._morph = data

		self.to_canonical = phi

		psi = FreeGroupMorphism('')
		psi._domain = self.F_canonical
		psi._codomain = self.F
		data = {}
		for x in self.F.gens():
			data[phi(x)] = x
			data[phi(x).inverse()] = x.inverse()
		psi._morph = data
		self.from_canonical = psi

		self.ws_canonical = [w.apply(phi) for w in self.ws]

	def isomorphism(self, other):
		if self.F.rank() != other.F.rank():
			return None
		iso = whitehead_equivalent(self.ws_canonical, other.ws_canonical)
		if iso != None:
			iso = other.from_canonical * iso * self.to_canonical
		return iso

	def is_isomorphic(self, other):
		return self.isomorphism(other) != None

	def apply(self, phi):
		if phi._domain == self.F:
			ws = [phi(w.gen) for w in self.ws]
		elif phi._domain == self.F_canonical:
			ws = [phi(w.gen) for w in self.ws_canonical]
		else:
			raise Exception('Cannot apply phi to this group pair. Domain mismatch.')

		return GroupPair(phi._codomain, ws)