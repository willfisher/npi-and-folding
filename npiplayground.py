from labels import *
from face import *
from complex import Complex, Morphism as ComplexMorphism
from graph import Graph, Morphism as GraphMorphism
from facialtree import *
from folding import fold_complex_morphism
from presentation import Presentation


# Presentation complex associated to < a, b | b, b*a*b^-1*a^-2 >
P = Presentation.from_strings(['a', 'b'], ['b', 'baBAA'])
X = P.complex()

f = Complex.disc_diagram(X, X.faces[0], 1)
proj, imm = fold_complex_morphism(f)

children = get_children(X, imm)
#child = next(filter(lambda child: len(child.domain.G.vertices) == 3, children))

#children = get_children(X, child)

for child in children:
	print(child.domain)
	print(f'Chi: {child.domain.chi()}')
	print(f'Is Immersion: {child.is_immersion()}')
	print('---------------')
	child.f.visualize()