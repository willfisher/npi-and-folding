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

	def __repr__(self):
		rel_strs = []
		for rel in self.relations:
			res = ''
			prev = None
			count = 0
			for g, i in rel:
				if g == prev:
					count += i
				else:
					if prev != None:
						if count != 0:
							if count == 1:
								res += f'{prev}*'
							else:
								res += f'{prev}^{count}*'
					count = i
				prev = g
			if count != 0:
				if count == 1:
					res += prev
				else:
					res += f'{prev}^{count}'
			rel_strs.append(res.rstrip('*'))

		gen_str = ', '.join(self.generators)
		rel_str = ', '.join(rel_strs)
		return f'< {gen_str} | {rel_str} >'