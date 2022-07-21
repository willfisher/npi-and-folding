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
	def disc_diagram(X, face):
		if face not in X.faces:
			raise Exception('Face must be a face of X to construct disc diagram.')

		D = Complex.disc(len(face))
		D_face = D.faces[0]

		face_maps = SetFunction({D_face:FaceMap(D_face, face, 0, 1)})

		edges = D_face.face
		vertices = [e.initial for e in edges]
		f_V = SetFunction({vertices[i]:face.face[i].initial for i in range(len(face))})
		f_E = SetFunction({edges[i]:face.face[i] for i in range(len(face))})
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
		curr = next(iter(C.edges))
		for i in range(n):
			C_face.append(curr)
			curr = next(iter(C.out_edges(curr.terminal)))
		C_face = Face(C_face)

		D = Complex(C, [C_face])
		return D

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
		curr = 0
		for _ in range(len(self.origin.face)):
			self.indice_map[(curr + self.origin_start_index) % len(self.origin.face)] = (curr + self.start_index) % len(self.target.face)
			curr += self.orientation

	@staticmethod
	def from_indice_map(origin, target, indice_map):
		start_index = indice_map[0]
		orientation = 1 if (len(origin.face) == 1 or (indice_map[1] - indice_map[0] - 1) % len(target.face) == 0) else -1
		return FaceMap(origin, target, start_index, orientation)

	# The composite f circ g
	@staticmethod
	def compose(f, g):
		if g.target != f.origin:
			raise Exception('Tried composing two incomposible face maps.')

		indice_map = {}
		for i in range(len(g.origin.face)):
			indice_map[i] = f.indice_map[g.indice_map[i]]

		return FaceMap.from_indice_map(g.origin, f.target, indice_map)


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
			raise Exception('Face map does not have right domain or codomain.')

		if not (f.domain == domain.G and f.codomain == codomain.G):
			raise Exception('Skeleta map does not have right domain or codomain.')

		# Commutivity of facemaps with skeleta map
		for facemap in self.face_maps.values():
			for i, j in facemap.indice_map.items():
				if not f.f_E[facemap.origin.face[i]] == facemap.target.face[j]:
					raise Exception('Face maps must commute with skeleta map to define morphism of complexes.')

	def is_immersion(self):
		return self.f.is_immersion() and all(map(lambda fm: fm.degree() == 1, self.face_maps.values()))

	def __eq__(self, other):
		if not isinstance(other, Morphism):
			return False

		return self.domain == other.domain and self.codomain == other.codomain and self.f == other.f and self.face_maps == other.face_maps

	# The composite f circ g
	@staticmethod
	def compose(f, g):
		face_maps = SetFunction()
		for face, g_map in g.face_maps.items():
			face_maps[face] = FaceMap.compose(f.face_maps[g_map.target], g_map)
		return Morphism(g.domain, f.codomain, GraphMorphism.compose(f.f, g.f), face_maps)

	@staticmethod
	def identity(X):
		face_maps = SetFunction({f:FaceMap(f, f, 0, 1) for f in X.faces})
		return Morphism(X, X, GraphMorphism.identity(X.G), face_maps)


