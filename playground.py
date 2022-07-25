from graph import *
from setfunction import SetFunction
from commongraphs import *
from complex import Complex
from complex import Morphism as ComplexMorphism
from labels import *
from face import Face
from folding import *

'''
# Wrapping cycle example
n = 12
m = 6
G1 = cycle(n)
G2 = cycle(m)

V1 = list(G1.vertices)
V2 = list(G2.vertices)
f_V = SetFunction({V1[i]:V2[i % m] for i in range(len(V1))})
f_E = SetFunction({})
for v in G1.vertices:
	e1 = next(iter(G1.out_edges(v)))
	e2 = next(iter(G2.out_edges(f_V[v])))
	f_E[e1] = e2

f = Morphism(G1, G2, f_V, f_E)
print(f.is_immersion())

# Disjoint union test
G, incl1, incl2 = Graph.disjoint_union(G1, G2, include_arrows = True)
print(G)
'''

# Presentation complex associated to < a, b | b, b*a*b^-1*a^-2 >
v = Vertex(label = 'v')
a = Edge(v, v, label = 'a')
b = Edge(v, v, label = 'b')
G = Graph([v], [a, b], add_vertices_from_edges = False)
faces = [Face([b]), Face([b, a, G.bar(b), G.bar(a), G.bar(a)])]
X = Complex(G, faces)

ident = ComplexMorphism.identity(X)
#proj, imm = fold_complex_morphism(ident)
#assert ComplexMorphism.compose(imm, proj) == ident

f = Complex.disc_diagram(X, faces[1])
#proj, imm = fold_complex_morphism(f)
#print(f.is_immersion())

w = next(iter(f.domain.G.vertices))
g = ComplexMorphism.wedge(ident, v, f, w)
print(g.domain)


'''
# Graph folding
v = Vertex(label = 'v')
a = Edge(v, v, label = 'a')
b = Edge(v, v, label = 'b')
G = Graph([v], [a, b], add_vertices_from_edges = False)
_, f = Face([b, a, b, G.bar(b), b, a, G.bar(a)]).face_map(G)

proj, g = fold_graph_morphism(f)
print(f'f is immersion: {f.is_immersion()}') # False
print(f'g is immersion: {g.is_immersion()}') # True
print(Morphism.compose(g, proj) == f)
'''
