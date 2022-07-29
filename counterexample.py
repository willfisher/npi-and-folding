from complex import Complex, Morphism as ComplexMorphism, FaceMap
from presentation import Presentation
from graph import Graph, Morphism as GraphMorphism
from labels import *
from face import Face
from setfunction import *

P = Presentation.from_strings(['a', 'b'], ['abbaB', 'baBAA'])
X = P.complex()

# Extract faces and edges from X
v = next(iter(X.G.vertices))
a, b = list(X.G.orientation)
if a.label == 'b':
	a, b = b, a

ai, bi = X.G.bar(a), X.G.bar(b)
alpha, beta = X.faces
if alpha[0] == b:
	alpha, beta = beta, alpha

# Construct counter example
v0 = Vertex('0')
v1 = Vertex('1')
v2 = Vertex('2')
v3 = Vertex('3')
e1 = Edge(v0, v2, label = 'e1')
e2 = Edge(v1, v2, label = 'e2')
e3 = Edge(v3, v1, label = 'e3')
e4 = Edge(v3, v0, label = 'e4')
e5 = Edge(v1, v0, label = 'e5')
e6 = Edge(v2, v2, label = 'e6')
e7 = Edge(v3, v1, label = 'e7')
e8 = Edge(v0, v3, label = 'e8')
Y_skeleton = Graph([v0, v1, v2, v3], [e1, e2, e3, e4, e5, e6, e7, e8])

f1 = Face([Y_skeleton.bar(e1), Y_skeleton.bar(e4), e3, e2, e6])
f2 = Face([e5, e8, e4, e1, Y_skeleton.bar(e2)])
f3 = Face([e8, e3, e5, e8, e4])
f4 = Face([e2, Y_skeleton.bar(e6), Y_skeleton.bar(e6), Y_skeleton.bar(e1), Y_skeleton.bar(e5)])
f5 = Face([e7, e2, Y_skeleton.bar(e6), Y_skeleton.bar(e2), Y_skeleton.bar(e3)])
f6 = Face([e7, e5, Y_skeleton.bar(e4), e7, Y_skeleton.bar(e3)])

Y = Complex(Y_skeleton, [f1, f2, f3, f4, f5, f6])

# Construct the immersion
face_maps = SetFunction()
face_maps[f1] = FaceMap(f1, alpha, 0, 1)
face_maps[f2] = FaceMap(f2, beta, 0, 1)
face_maps[f3] = FaceMap(f3, alpha, 0, 1)
face_maps[f4] = FaceMap(f4, alpha, 0, 1)
face_maps[f5] = FaceMap(f5, beta, 0, -1)
face_maps[f6] = FaceMap(f6, alpha, 0, 1)

f_V = SetFunction({w:v for w in Y_skeleton.vertices})
f_E = SetFunction({e1:ai, e2:a, e3:b, e4:bi, e5:b, e6:bi, e7:a, e8:a})
f = GraphMorphism(Y_skeleton, X.G, f_V, f_E)

imm = ComplexMorphism(Y, X, f, face_maps)

print(f'chi(Y) = {Y.chi()}')
print(f'Is Immersion: {imm.is_immersion()}')

