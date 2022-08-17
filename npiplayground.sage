from labels import *
from face import *
from complex import Complex, Morphism as ComplexMorphism
from graph import Graph, Morphism as GraphMorphism
from facialtree import *
from folding import fold_complex_morphism
from presentation import Presentation
from freefaceresolver import *

# Presentation complex associated to < a, b | b, b*a*b^-1*a^-2 >
n = 1
# Contractible if b exponent sum is 1
w = 'b'
P = Presentation.from_strings(['a', 'b'], [w, 'b' + 'a'*n + 'B' + 'A'*(n + 1)])
X = P.complex()

load('checknpi.sage')
assert is_trivial(pres_to_sage(X.presentation()))

f = Complex.disc_diagram(X, X.faces[0], 1)
proj, imm = fold_complex_morphism(f)


import random
depth = 15
while True:
	parent = imm
	for d in range(depth):
		children = get_children(X, parent, check_npi = check_npis)
		print(f'Depth: {d}')

		parent = random.choice(children)

# Free face resolution
#resolutions = resolve_free_faces(imm, max_depth = 100, max_resolutions = 1000, check_npi = check_npis)
#print(len(resolutions))