from commongraphs import cycle
from setfunction import SetFunction
from graph import Morphism

class Face:
	counter = 0
	def __init__(self, face):
		self.face = face
		self.uid = Face.counter
		Face.counter += 1

	def face_map(self, G):
		for e in self.face:
			if not e in G.edges:
				raise Exception('Can only attach a face to a graph which contains its attaching edges.')

		C = cycle(len(self.face))
		v_curr = next(iter(C.vertices))
		v0 = v_curr
		e_curr = next(iter(C.out_edges(v_curr)))
		f_V = SetFunction()
		f_E = SetFunction()
		for i in range(len(self.face)):
			e = self.face[i]
			f_V[v_curr] = e.initial
			f_E[e_curr] = e

			v_curr = e_curr.terminal
			e_curr = next(iter(C.out_edges(v_curr)))

		return v0, Morphism(C, G, f_V, f_E)

	'''
		Checks if two faces are equal up to cycling their elements and orientation.
		Returns the positive index offset s.t. f1[i] = f2[orientation * i + offset] for all i if true, else -1.
	'''
	@staticmethod
	def offset_equal(f1, f2):
		if len(f1.face) != len(f2.face):
			return -1, 0

		for offset in range(len(f1.face)):
			for orientation in [1, -1]:
				worked = True
				for i in range(len(f1.face)):
					ind = i + offset if orientation == 1 else (-1 - i) + offset
					ind = ind % len(f2.face)
					if f1.face[i] != f2.face[ind]:
						worked = False
						break
				if worked:
					return offset, orientation
		return -1, 0

	def copy(self, edge_map = {}, vertex_map = {}):
		return Face([edge_map.get(e, e.copy(vertex_map = vertex_map)) for e in self.face])

	def __len__(self):
		return len(self.face)

	def __getitem__(self, key):
		return self.face[key]

	def __iter__(self):
		for elem in self.face:
			yield elem

	def __eq__(self, other):
		if not isinstance(other, Face):
			return False
		return self.uid == other.uid

	def __hash__(self):
		return hash(f'Face{self.uid}')

	def __repr__(self):
		return self.face.__repr__()