from labels import *
from face import *
from complex import Complex, Morphism as ComplexMorphism
from graph import Graph, Morphism as GraphMorphism
from facialtree import *
from folding import fold_complex_morphism


# Presentation complex associated to < a, b | b, b*a*b^-1*a^-2 >
v = Vertex(label = 'v')
a = Edge(v, v, label = 'a')
b = Edge(v, v, label = 'b')
G = Graph([v], [a, b], add_vertices_from_edges = False)
faces = [Face([b]), Face([b, a, G.bar(b), G.bar(a), G.bar(a)])]
X = Complex(G, faces)

f = Complex.disc_diagram(X, faces[0])
proj, imm = fold_complex_morphism(f)

children = get_children(X, imm)

for child in children:
	print(child.domain)
	print(f'Chi: {child.domain.chi()}')
	print(f'Is Immersion: {child.is_immersion()}')
	print('---------------')
	child.domain.G.visualize()