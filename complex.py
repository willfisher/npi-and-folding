from graph import Graph
from graph import Morphism as GraphMorphism
from setfunction import SetFunction
from commongraphs import cycle, empty_graph
from face import Face

class Complex:
	'''
		G should be 1-skeleton and faces should be a list of lists of edges representing the boundaries of faces.
	'''
	def __init__(self, G, faces):
		self.G = G
		self.faces = faces

		if not all(map(lambda face: face.mapsto(G), faces)):
			raise Exception('All faces must map to 1-skeleton.')


	def chi(self):
		return self.G.chi() + len(self.faces)

	
	# Constructs a morphism from a disjoint union of cycles to the skeleton
	@staticmethod
	def construct_face_map(G, faces):
		S = empty_graph()
		w = GraphMorphism(S, G, SetFunction(), SetFunction())
		start_vertices = {}
		for face in faces:
			v0, f = face.face_map(G)
			w = GraphMorphism.disjoint_union(w, f)
			start_vertices[face] = v0

		return w.domain, w, start_vertices

	'''
		Returns the complex morphism representing attaching a disc to the face `face`.
	'''
	@staticmethod
	def disc_diagram(X, face, orientation):
		orientation = 1 if orientation >= 0 else -1
		if face not in X.faces:
			raise Exception('Face must be a face of X to construct disc diagram.')

		D = Complex.disc(len(face))
		D_face = D.faces[0]

		fm = FaceMap(D_face, face, 0, orientation)
		face_maps = SetFunction({D_face:fm})

		edges = D_face.face
		vertices = [e.initial for e in edges]
		f_V = SetFunction({vertices[i]:fm.eval(X.G, i).initial for i in range(len(face))})
		f_E = SetFunction({edges[i]:fm.eval(X.G, i) for i in range(len(face))})
		f_skeleta = GraphMorphism(D.G, X.G, f_V, f_E)
		f = Morphism(D, X, f_skeleta, face_maps)

		return f

	'''
		Get a disc with n edges
	'''
	@staticmethod
	def disc(n, include_labels = False):
		C = cycle(n)
		C_face = []
		curr = next(iter(C.orientation))
		for i in range(n):
			C_face.append(curr)
			curr = next(iter(C.out_edges(curr.terminal)))
		C_face = Face(C_face)

		D = Complex(C, [C_face])
		return D

	# Make a copy of a graph. Optionally include mappings between old/new vertex/edge sets
	def copy(self, include_maps = False, maps_only = False, vertex_map = {}):
		G, newV, newE = self.G.copy(include_maps = include_maps, maps_only = False, vertex_map = vertex_map)
		if maps_only:
			return newV, newE

		faces = [face.copy(edge_map = newE) for face in self.faces]

		X = Complex(G, faces)
		if not include_maps:
			return X
		return X, newV, newE

	'''
		Wedges two complexes together at specified vertices
	'''
	@staticmethod
	def wedge(X1, v1, X2, v2, include_maps = False):
		if not (v1 in X1.G.vertices and v2 in X2.G.vertices):
			raise Exception('Vertices must belong to respective complexes to form wedge.')

		G, incl1, incl2 = Graph.wedge(X1.G, v1, X2.G, v2, include_maps = True)

		faces = [face.copy(edge_map = incl1.f_E) for face in X1.faces] + [face.copy(edge_map = incl2.f_E) for face in X2.faces]

		X = Complex(G, faces)
		if not include_maps:
			return X

		face_maps1 = SetFunction({face:FaceMap(face, faces[i], 0, 1) for i, face in enumerate(X1.faces)})
		face_maps2 = SetFunction({face:FaceMap(face, faces[i + len(X1.faces)], 0, 1) for i, face in enumerate(X2.faces)})

		incl1 = Morphism(X1, X, incl1, face_maps1)
		incl2 = Morphism(X2, X, incl2, face_maps2)

		return X, incl1, incl2

	'''
		Get the free faces of this complex.
	'''
	def free_faces(self):
		counts = {}
		faces = {}
		for face in self.faces:
			for e in face:
				e_canon = self.G.oriented(e)
				counts[e_canon] = counts.get(e_canon, 0) + 1
				faces[e_canon] = face

		return [(e, faces[e]) for e, c in counts.items() if c == 1]

	'''
		Checks if edge is free face.
	'''
	def is_free_face(self, e):
		return self.G.oriented(e) in map(lambda p: p[0], self.free_faces())

	def has_free_faces(self):
		return len(self.free_faces()) > 0


	def __eq__(self, other):
		if not isinstance(other, Complex):
			return False

		return self.faces == other.faces and self.G == other.G

	def __repr__(self):
		return f'1-skeleton:\n{self.G}\nFaces: {self.faces}'

'''
	Represents an immersion of a face (given by a cycle) onto another face.
	Orientiation should be +1 or -1
'''
class FaceMap:
	def __init__(self, origin, target, start_index, orientation, origin_start_index = 0):
		self.origin = origin
		self.target = target
		self.start_index = start_index
		self.orientation = 1 if orientation > 0 else -1
		self.origin_start_index = origin_start_index

		if len(self.origin.face) % len(self.target.face) != 0:
			raise Exception('Face maps must be coverings.')

		self.indice_map = {}
		im_curr = 0 if orientation == 1 else -1
		dom_curr = 0
		for _ in range(len(self.origin.face)):
			self.indice_map[(dom_curr + self.origin_start_index) % len(self.origin.face)] = (im_curr + self.start_index) % len(self.target.face)
			im_curr += self.orientation
			dom_curr += 1

	# The composite f circ g
	@staticmethod
	def compose(f, g):
		if g.target != f.origin:
			raise Exception('Tried composing two incomposible face maps.')

		start_index = f.initial(g.initial(0))

		return FaceMap(g.origin, f.target, start_index, f.orientation * g.orientation)

	'''
		Evaluates the image of index i edge of target inside G
	'''
	def eval(self, G, i):
		ind = self.indice_map[i]
		e = self.target[ind]
		if self.orientation == -1:
			e = G.bar(e)
		return e

	'''
		Gives the initial vertex of the image of edge i in the origin.
	'''
	def initial(self, i):
		j = self.indice_map[i]
		if self.orientation == 1:
			res = j
		else:
			res = j + 1
		return res % len(self.target)

	# Same as above but for terminal.
	def terminal(self, i):
		j = self.indice_map[i]
		if self.orientation == 1:
			res = j + 1
		else:
			res = j
		return res % len(self.target)


	def __getitem__(self, key):
		return self.indice_map[key]

	def degree(self):
		return len(self.origin.face) // len(self.target.face)

	def __hash__(self):
		return hash(f'{self.origin}|{self.target}|{self.start_index}|{self.orientation}|{self.origin_start_index}')

	def __eq__(self, other):
		if not isinstance(other, FaceMap):
			return False

		return self.origin == other.origin and self.target == other.target and self.start_index == other.start_index \
			and self.orientation == other.orientation and self.origin_start_index == other.origin_start_index


'''
	Morphism of complexes. f and s are graph morphisms between the 1-skeleta and attaching maps respectively.
	Facemaps should be a set function
'''
class Morphism:
	def __init__(self, domain, codomain, f, face_maps):
		self.domain = domain
		self.codomain = codomain
		self.f = f
		self.face_maps = face_maps

		# Basic checks
		if face_maps.domain != set(domain.faces):
			raise Exception('Face map was not given for each face in domain.')

		if not set(map(lambda fm: fm.target, face_maps.values())).issubset(codomain.faces):
			raise Exception('Face maps don\'t map to faces of the codomain.')

		if not (f.domain == domain.G and f.codomain == codomain.G):
			raise Exception('Skeleta map does not have right domain or codomain.')

		if not all(map(lambda p: p[0] == p[1].origin, face_maps.items())):
			raise Exception('Face maps must be indexed by their origin face.')

		# Commutivity of facemaps with skeleta map
		for facemap in self.face_maps.values():
			for i in range(len(facemap.origin)):
				if not f.f_E[facemap.origin.face[i]] == facemap.eval(codomain.G, i):
					e1 = f.f_E[facemap.origin.face[i]]
					e2 = facemap.eval(codomain.G, i)
					print(f'{e1}@{e1.uid} {e2}@{e2.uid}')
					raise Exception('Face maps must commute with skeleta map to define morphism of complexes.')

	'''
		Factors a map through a wedge if possible.
	'''
	@staticmethod
	def wedge(f1, v1, f2, v2, include_maps = False):
		if v1 not in f1.domain.G.vertices or v2 not in f2.domain.G.vertices:
			raise Exception('Vertices must belong to respective domains to form wedge of morphisms.')
		if f1.f.f_V[v1] != f2.f.f_V[v2]:
			raise Exception('Morphisms must agree at wedge vertices to factor through wedge.')
		if f1.codomain != f2.codomain:
			raise Exception('Morphisms must have the same codomoin to factor through wedge.')

		X1 = f1.domain
		X2 = f2.domain
		X, incl1, incl2 = Complex.wedge(X1, v1, X2, v2, include_maps = True)
		f_V = SetFunction()
		f_E = SetFunction()
		for v in X1.G.vertices:
			f_V[incl1.f.f_V[v]] = f1.f.f_V[v]
		for v in X2.G.vertices:
			f_V[incl2.f.f_V[v]] = f2.f.f_V[v]
		for e in X1.G.edges:
			f_E[incl1.f.f_E[e]] = f1.f.f_E[e]
		for e in X2.G.edges:
			f_E[incl2.f.f_E[e]] = f2.f.f_E[e]

		f_skeleta = GraphMorphism(X.G, f1.codomain.G, f_V, f_E)

		face_maps = SetFunction()
		for face in X1.faces:
			wedge_face = incl1.face_maps[face].target
			fm = f1.face_maps[face]
			face_maps[wedge_face] = FaceMap(wedge_face, fm.target, fm.start_index, fm.orientation)
		for face in X2.faces:
			wedge_face = incl2.face_maps[face].target
			fm = f2.face_maps[face]
			face_maps[wedge_face] = FaceMap(wedge_face, fm.target, fm.start_index, fm.orientation)

		f = Morphism(X, f1.codomain, f_skeleta, face_maps)
		if not include_maps:
			return f
		return f, incl1, incl2


	def is_immersion(self):
		return self.is_branched_immersion() and all(map(lambda fm: fm.degree() == 1, self.face_maps.values()))

	def is_branched_immersion(self):
		if not self.f.is_immersion():
			return False

		# Checks if S_Y -> Y_(1) x_{X_(1)} S_X is injective
		seen = set()
		for face, fm in self.face_maps.items():
			for i, e in enumerate(face):
				val1 = (e, (fm.target, fm[i], fm.orientation))
				val2 = (self.domain.G.bar(e), (fm.target, fm[i], -fm.orientation))
				if val1 in seen or val2 in seen:
					return False
				seen.add(val1)
				seen.add(val2)

		return True


	def __eq__(self, other):
		if not isinstance(other, Morphism):
			return False

		return self.domain == other.domain and self.codomain == other.codomain and self.f == other.f and self.face_maps == other.face_maps

	# The composite f circ g
	@staticmethod
	def compose(f, g):
		if f.domain != g.codomain:
			raise Exception('Trying to compose functions without compatible domain/codomain.')

		face_maps = SetFunction()
		for face, g_map in g.face_maps.items():
			face_maps[face] = FaceMap.compose(f.face_maps[g_map.target], g_map)
		return Morphism(g.domain, f.codomain, GraphMorphism.compose(f.f, g.f), face_maps)

	@staticmethod
	def identity(X):
		face_maps = SetFunction({f:FaceMap(f, f, 0, 1) for f in X.faces})
		return Morphism(X, X, GraphMorphism.identity(X.G), face_maps)


