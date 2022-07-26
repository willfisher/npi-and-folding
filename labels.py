class Vertex:
	counter = 0
	def __init__(self, label = ''):
		self.label = str(label)
		self.uid = Vertex.counter
		Vertex.counter += 1

	def __eq__(self, other):
		if not isinstance(other, Vertex):
			return False
		return self.uid == other.uid

	def __hash__(self):
		return hash(f'Vertex{self.uid}')

	def __repr__(self):
		return self.label

	def copy(self):
		return Vertex(label = self.label)

class Edge:
	counter = 0
	def __init__(self, initial, terminal, label = ''):
		self.label = str(label)
		self.uid = Edge.counter
		Edge.counter += 1

		self.initial = initial
		self.terminal = terminal

	def __eq__(self, other):
		if not isinstance(other, Edge):
			return False
		return self.uid == other.uid

	def __hash__(self):
		return hash(f'Edge{self.uid}')

	def __repr__(self):
		return self.label + f'({self.initial} -> {self.terminal})'

	def bar(self):
		return Edge(self.terminal, self.initial, label = self.label + 'i')

	def copy(self, vertex_map = {}, vertex_copy = False):
		v1 = self.initial
		v2 = self.terminal
		if v1 in vertex_map:
			v1 = vertex_map[v1]
		elif vertex_copy:
			v1 = v1.copy()
		if v2 in vertex_map:
			v2 = vertex_map[v2]
		elif vertex_copy:
			v2 = v2.copy()
		return Edge(v1, v2, label = self.label)