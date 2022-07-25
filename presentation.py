from complex import Complex
from labels import *
from graph import Graph
from face import Face

class Presentation:
	def __init__(self, generators, relations):
		self.generators = generators
		self.relations = relations

	@staticmethod
	def from_strings(generators, relations):
		transform = lambda rel: [(str(char).lower(), 1 if str(char).islower() else -1) for char in rel]
		relations = list(map(transform, relations))
		return Presentation(generators, relations)

	def complex(self):
		v = Vertex(label = 'v')
		edges = {gen:Edge(v, v, label = gen) for gen in self.generators}

		G = Graph([v], set(edges.values()), add_vertices_from_edges = False)
		faces = [Face([edges[g[0]] if g[1] == 1 else G.bar(edges[g[0]]) for g in rel]) for rel in self.relations]

		X = Complex(G, faces)
		return X