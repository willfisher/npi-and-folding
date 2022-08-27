from train_track import *
import itertools
from multiset import Multiset

def cyclically_reduced(w):
	F = w.parent()
	tietze = w.Tietze()
	while len(tietze) >= 2 and tietze[0] == -tietze[-1]:
		tietze = tietze[1:-1]

	return F(tietze)

def cyclically_equal(w1, w2):
	w1 = w1.Tietze()
	w2 = w2.Tietze()
	if len(w1) != len(w2):
		return False

	for i in range(len(w1)):
		if w1[i:] + w1[:i] == w2:
			return True

	return False

def word_length(w):
	return len(w.Tietze())

def whitehead_score(elem):
	return sum(map(len, elem))

'''
	Represents the conjugacy class of < gen >
'''
class ConjCyclicSubgroup:
	def __init__(self, gen):
		self.gen = cyclically_reduced(gen)

	def __eq__(self, other):
		if not isinstance(other, ConjCyclicSubgroup):
			return False

		return cyclically_equal(self.gen, other.gen) or cyclically_equal(self.gen, other.gen.inverse())

	def __len__(self):
		return word_length(self.gen)

	def __hash__(self):
		return hash(self.gen) + hash(self.gen.inverse())

	def __repr__(self):
		return f'C(<{self.gen}>)'

	def apply(self, phi):
		return ConjCyclicSubgroup(phi(self.gen))

'''
	Returns an automorphism taking the set elem1 to elem2 if one exists.
'''
def whitehead_equivalent(elem1, elem2, whitehead_autos = None):
	elem1 = list(elem1)
	elem2 = list(elem2)
	if len(elem1) != len(elem2):
		return None

	if len(elem1) == 0:
		return FreeGroupAutomorphism('')

	F = elem1[0].gen.parent()
	if F != elem2[0].gen.parent():
		raise Exception('Cyclic subgroups must belong to the same parent subgroup.')
	
	if not whitehead_autos:
		autos = whitehead_automorphisms(F)
	else:
		autos = whitehead_autos

	elem1_reduced, psi1 = whitehead_reduce(elem1, whitehead_autos = autos)
	elem2_reduced, psi2 = whitehead_reduce(elem2, whitehead_autos = autos)

	if Multiset(map(len, elem1_reduced)) != Multiset(map(len, elem2_reduced)):
		return None

	# Now branch out tree to try and find elem2_reduced in component of elem1_reduced
	elem1_reduced = Multiset(elem1_reduced)
	elem2_reduced = Multiset(elem2_reduced)
	if elem1_reduced == elem2_reduced:
		return psi2.inverse()*psi1

	N = whitehead_score(elem1_reduced)
	ident = FreeGroupAutomorphism.identity_automorphism(F)
	found = [(elem1_reduced, ident)]
	while True:
		found_new = False
		for elem, nu in found:
			for mu in itertools.chain(*autos):
				_elem = Multiset(v.apply(mu) for v in elem)
				if whitehead_score(_elem) != N:
					continue
				if not any(map(lambda p: p[0] == _elem, found)):
					if _elem == elem2_reduced:
						return psi2.inverse()*mu*nu*psi1
					found.append((_elem, mu*nu))
					found_new = True
		if not found_new:
			break

	return None


'''
	Whitehead reduces a tuple of conjugacy classes of cyclic subgroups and returns the reducing automorphism.
'''
def whitehead_reduce(elem, whitehead_autos = None):
	if len(elem) == 0:
		return elem

	F = elem[0].gen.parent()
	if not whitehead_autos:
		type1, type2 = whitehead_automorphisms(F)
	else:
		type1, type2 = whitehead_autos

	psi = FreeGroupAutomorphism.identity_automorphism(F)
	while True:
		score = whitehead_score(elem)
		decreased = False
		for phi in type2:
			_elem = [v.apply(phi) for v in elem]
			_score = whitehead_score(_elem)
			if _score < score:
				score = _score
				elem = _elem
				psi = phi*psi
				decreased = True
		if not decreased:
			break
	return elem, psi

'''
	Construct all distinct Whitehead automorphisms of F.
'''
def whitehead_automorphisms(F):
	X = F.gens()
	Xpm = list(X) + [x.inverse() for x in X]

	type2 = []
	for choices in itertools.product(range(4), repeat = len(X) - 1):
		for a in Xpm:
			data = {a: a}
			i = 0
			for v in X:
				if v == a or v.inverse() == a:
					continue
				choice = choices[i]
				if choice == 0:
					data[v] = v
				elif choice == 1:
					data[v] = v*a
				elif choice == 2:
					data[v] = a.inverse()*v
				elif choice == 3:
					data[v] = a.inverse()*v*a
				i += 1
			phi = dict_to_morphism(data)
			if phi not in type2:
				type2.append(phi)

	type1 = []
	for perm in itertools.permutations(range(len(X))):
		data = {v:X[perm[i]] for i, v in enumerate(X)}
		type1.append(dict_to_morphism(data))

	return type1, type2

# Convert a dict directly to FreeGroupAutomorphism object instead of converting everything to strings.
def dict_to_morphism(data):
	phi = FreeGroupMorphism('')
	k, v = next(iter(data.items()))
	domain = k.parent()
	codomain = v.parent()
	phi._domain = domain
	phi._codomain = codomain

	for v in domain.gens():
		if not (v in data or v.inverse() in data):
			raise Exception('Morphism is underdefined.')
		if v.inverse() not in data:
			data[v.inverse()] = data[v].inverse()
		if v not in data:
			data[v] = data[v.inverse()].inverse()
	phi._morph = data

	return FreeGroupAutomorphism(phi)