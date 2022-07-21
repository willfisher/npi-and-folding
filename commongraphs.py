from graph import Graph
from labels import Edge, Vertex

def cycle(n):
	vertices = {i:Vertex(i) for i in range(n)}
	return Graph([], [Edge(vertices[i], vertices[(i + 1) % n]) for i in range(n)])

def empty_graph():
	return Graph([], [])