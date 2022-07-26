from setfunction import SetFunction
from labels import Edge, Vertex
import itertools

class Graph:
	def __init__(self, vertices, edges, add_vertices_from_edges = True):
		self.vertices = set(vertices)
		self.edges = set(edges)

		if not all(map(lambda p: isinstance(p, Edge), self.edges)):
			raise Exception('Edges should be a list of Edge objects.')

		# Add unrecognized vertices appearing in edges
		if add_vertices_from_edges:
			for e in self.edges:
				i, j = e.initial, e.terminal
				if i not in self.vertices:
					self.vertices.add(i)
				if j not in self.vertices:
					self.vertices.add(j)

		# Assume default orientation
		self.orientation = self.edges.copy()

		# Populate the bar edges
		self.bar_map = {}
		bar_edges = set()
		for e in self.edges:
			e_bar = e.bar()
			self.bar_map[e] = e_bar
			self.bar_map[e_bar] = e
			bar_edges.add(e_bar)
		self.edges |= bar_edges

	def oriented(self, e):
		if e not in self.orientation:
			e = self.bar(e)

		return e

	def matches_orientation(self, e):
		return e in self.orientation

	def chi(self):
		return len(self.vertices) - len(self.orientation)

	def bar(self, edge):
		return self.bar_map[edge]

	def remove_vertex(self, v, remove_edges = True):
		self.vertices.discard(v)
		if remove_edges:
			for e in self.edges:
				if e.initial == v or e.terminal == v:
					self.remove_edge(e)

	def remove_edge(self, e):
		if e not in self.edges:
			return
		e_bar = self.bar(e)
		self.orientation.discard(e)
		self.orientation.discard(e_bar)
		self.edges.discard(e)
		self.edges.discard(e_bar)
		del self.bar_map[e]
		del self.bar_map[e_bar]

	# Returns the edges incident at v
	def neighborhood(self, v):
		nbhd = set()
		for e in self.edges:
			if e.initial == v:
				nbhd.add(e)
		return nbhd

	# Returns out edges wrt orientation
	def out_edges(self, v):
		return self.neighborhood(v).intersection(self.orientation)

	# Returns in edges wrt orientation
	def in_edges(self, v):
		return self.neighborhood(v).difference(self.orientation)

	# Returns whether the graph is a disjoint union of cycles
	def is_open_linear(self):
		for v in self.vertices:
			if not len(self.neighborhood(v)) == 2:
				return False
		return True

	# Make a copy of a graph. Optionally include mappings between old/new vertex/edge sets
	def copy(self, include_maps = False, maps_only = False, vertex_map = {}):
		newV = {v:vertex_map.get(v, v.copy()) for v in self.vertices}
		newE = {e:e.copy(vertex_map = newV) for e in self.orientation}
		if maps_only:
			return newV, newE
		G = Graph(set(newV.values()), set(newE.values()), add_vertices_from_edges = False)
		if not include_maps:
			return G
		return G, newV, newE

	@staticmethod
	def wedge(G1, v1, G2, v2, include_maps = False):
		if v1 not in G1.vertices or v2 not in G2.vertices:
			raise Exception('Vertices must belong to respective graphs to form wedge.')

		w = v1.copy()
		vertex_map = {v1:w, v2:w}

		newV1, newE1 = G1.copy(maps_only = True, vertex_map = vertex_map)
		newV2, newE2 = G2.copy(maps_only = True, vertex_map = vertex_map)

		G = Graph(set(newV1.values()) | set(newV2.values()), set(newE1.values()) | set(newE2.values()), add_vertices_from_edges = False)
		if not include_maps:
			return G

		f1 = Morphism(G1, G, SetFunction(newV1), SetFunction(newE1))
		f2 = Morphism(G2, G, SetFunction(newV2), SetFunction(newE2))

		return G, f1, f2

	@staticmethod
	def disjoint_union(G1, G2, include_arrows = False):
		newV1, newE1 = G1.copy(maps_only = True)
		newV2, newE2 = G2.copy(maps_only = True)

		vertices = set(newV1.values()).union(set(newV2.values()))
		edges = set(newE1.values()).union(set(newE2.values()))

		G = Graph(vertices, edges, add_vertices_from_edges = False)
		if not include_arrows:
			return G

		f1 = Morphism(G1, G, SetFunction({v:newV1[v] for v in G1.vertices}), SetFunction({e:newE1[e] for e in G1.orientation}))
		f2 = Morphism(G2, G, SetFunction({v:newV2[v] for v in G2.vertices}), SetFunction({e:newE2[e] for e in G2.orientation}))

		return G, f1, f2

	def visualize(self, edge_labels = {}, vertex_labels = {}):
		from graphvisualization import GraphVisualization
		visual = GraphVisualization.from_graph(self, edge_labels = edge_labels, vertex_labels = vertex_labels)
		visual.visualize()

	'''
		Gets a spanning tree of the component of the vertex v based at v.
	'''
	def spanning_tree(self, v):
		seen = set([v])
		edges = set()
		to_check = [v]
		while len(to_check) > 0:
			new_to_check = []
			for w in to_check:
				out_edges = self.neighborhood(w)
				for e in out_edges:
					ww = e.terminal
					if ww not in seen:
						seen.add(ww)
						edges.add(e)
						new_to_check.append(ww)

			to_check = new_to_check

		# Manually set T so that it strictly a subgraph of self
		T = Graph([], [])
		T.vertices = seen
		T.orientation = edges.copy()
		edges |= set([self.bar(e) for e in edges])
		bar_map = {e:self.bar_map[e] for e in edges}
		T.edges = edges
		T.bar_map = bar_map

		# Should be a tree
		if len(T.vertices) - len(T.orientation) != 1:
			raise Exception('Spanning tree call produced not a tree.')

		return T


	def __eq__(self, other):
		if not isinstance(other, Graph):
			return False

		return self.vertices == other.vertices and self.edges == other.edges and self.orientation == other.orientation

	def __repr__(self):
		return f'Vertices: {self.vertices}\nOrientation: {self.orientation}'

	'''
		Json serializes a graph.
	'''
	def json(self):
		bar_map = {e.uid:ee.uid for e,ee in self.bar_map.items()}
		edges = {e.uid:[e.initial.uid, e.terminal.uid] for e in self.edges}

		data = {}
		data['bar_map'] = bar_map
		data['edges'] = edges
		data['vertices'] = [v.uid for v in self.vertices]
		data['orientation'] = [e.uid for e in self.orientation]

		return data

	@staticmethod
	def load_json(data, uid_maps = False):
		vertices = {int(uid):Vertex(label = str(i)) for i, uid in enumerate(data['vertices'])}
		edges = {int(uid):Edge(vertices[e[0]], vertices[e[1]], label = str(i)) for i, (uid, e) in enumerate(data['edges'].items())}
		orientation = set(edges[int(uid)] for uid in data['orientation'])
		bar_map = {edges[int(k)]:edges[int(v)] for k,v in data['bar_map'].items()}
		_edges = set(edges.values())
		_vertices = set(vertices.values())

		G = Graph([], [])
		G.vertices = _vertices
		G.edges = _edges
		G.orientation = orientation
		G.bar_map = bar_map

		if not uid_maps:
			return G
		return G, vertices, edges

class Morphism:
	def __init__(self, domain, codomain, f_V, f_E):
		self.domain = domain
		self.codomain = codomain
		self.f_V = f_V
		self.f_E = f_E

		# Basic verification
		if not self.f_V.domain == self.domain.vertices:
			raise Exception('f_V does not have proper domain.')
		if not self.f_V.mapsto(self.codomain.vertices):
			raise Exception('f_V does not have proper codomain.')
		if not self.f_E.mapsto(self.codomain.edges):
			raise Exception('f_E does not have proper codomain.')
			
		# Extend in involution preserving way if f_E is only defined on the orientation of domain
		if self.f_E.domain == self.domain.orientation:
			for e in self.domain.orientation:
				f_E[self.domain.bar(e)] = self.codomain.bar(f_E[e])

		# Basic verification
		if not self.f_E.domain == self.domain.edges:
			raise Exception('f_E does not have proper domain.')

		# Preserves bar map
		for e in self.domain.edges:
			if not self.f_E[self.domain.bar(e)] == self.codomain.bar(f_E[e]):
				raise Exception('Edge map does not commute with edge involution.')

		# Preserves incidence maps
		for e in self.domain.edges:
			if not self.f_V[e.initial] == self.f_E[e].initial or not self.f_V[e.terminal] == self.f_E[e].terminal:
				raise Exception('Morphism does not respect edge incidence maps.')

	def is_immersion(self):
		for v in self.domain.vertices:
			for e1, e2 in itertools.product(self.domain.neighborhood(v), repeat = 2):
				if self.f_E[e1] == self.f_E[e2] and e1 != e2:
					return False
		
		return True

	# The composite f circ g
	@staticmethod
	def compose(f, g):
		if g.codomain != f.domain:
			raise Exception('Can\'t compose morphisms of graphs without matching domain/codomain.')

		h_V = SetFunction.compose(f.f_V, g.f_V)
		h_E = SetFunction.compose(f.f_E, g.f_E)

		return Morphism(g.domain, f.codomain, h_V, h_E)

	@staticmethod
	def identity(G):
		f_V = SetFunction({v:v for v in G.vertices})
		f_E = SetFunction({e:e for e in G.edges})
		return Morphism(G, G, f_V, f_E)

	'''
		Visualize a morphism.
	'''
	def visualize(self):
		edge_labels = {e:self.f_E[e].label for e in self.domain.orientation}
		vertex_labels = {v:self.f_V[v].label for v in self.domain.vertices}
		self.domain.visualize(edge_labels = edge_labels, vertex_labels = vertex_labels)

	def __eq__(self, other):
		if not isinstance(other, Morphism):
			return False

		if not (self.domain == other.domain and self.codomain == other.codomain):
			return False

		return self.f_V == other.f_V and self.f_E == other.f_E

	'''
		Given morphisms f1 : G1 -> H, f2 : G2 -> H, return the disjoint union f : G1 cup G2 -> H.
	'''
	@staticmethod
	def disjoint_union(f1, f2):
		if f1.codomain != f2.codomain:
			raise Exception('Disjoint unions of maps must have equal codomain.')

		G1 = f1.domain
		G2 = f2.domain
		G, incl1, incl2 = Graph.disjoint_union(G1, G2, include_arrows = True)

		f_V = SetFunction()
		for v in G1.vertices:
			f_V[incl1.f_V[v]] = f1.f_V[v]
		for v in G2.vertices:
			f_V[incl2.f_V[v]] = f2.f_V[v]

		f_E = SetFunction()
		for e in G1.edges:
			f_E[incl1.f_E[e]] = f1.f_E[e]
		for e in G2.edges:
			f_E[incl2.f_E[e]] = f2.f_E[e]

		return Morphism(G, f1.codomain, f_V, f_E)

	'''
		Serialize to json.
	'''
	def json(self):
		data = {}
		data['domain'] = self.domain.json()
		data['codomain'] = self.codomain.json()

		data['f_V'] = {v.uid:self.f_V[v].uid for v in self.f_V.keys()}
		data['f_E'] = {e.uid:self.f_E[e].uid for e in self.f_E.keys()}

		return data

	@staticmethod
	def load_json(data, uid_maps = False):
		domain, domain_v_map, domain_e_map = Graph.load_json(data['domain'], uid_maps = True)
		codomain, codomain_v_map, codomain_e_map = Graph.load_json(data['codomain'], uid_maps = True)

		f_V = SetFunction({domain_v_map[int(k)]:codomain_v_map[int(v)] for k,v in data['f_V'].items()})
		f_E = SetFunction({domain_e_map[int(k)]:codomain_e_map[int(v)] for k,v in data['f_E'].items()})

		f = Morphism(domain, codomain, f_V, f_E)

		if not uid_maps:
			return f

		return f, domain_v_map, domain_e_map, codomain_v_map, codomain_e_map

