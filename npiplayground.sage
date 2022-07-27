from labels import *
from face import *
from complex import Complex, Morphism as ComplexMorphism
from graph import Graph, Morphism as GraphMorphism
from facialtree import *
from folding import fold_complex_morphism
from presentation import Presentation
from freefaceresolver import *

def pres_to_sage(pres):
	G = FreeGroup(len(pres.generators))
	rels = [G([i*(pres.generators.index(g) + 1) for g, i in rel]) for rel in pres.relations]
	H = G/rels
	return H

def is_trivial(H):
	if len(H.abelian_invariants()) > 0:
		return False
	return H.cardinality(limit = 100000) == 1

def valid_npis(Y):
	if Y.chi() <= 0:
		return True
	if Y.chi() > 1:
		return False

	return is_trivial(pres_to_sage(Y.presentation()))

# Presentation complex associated to < a, b | b, b*a*b^-1*a^-2 >
P = Presentation.from_strings(['a', 'b'], ['b', 'baBAA'])
X = P.complex()

f = Complex.disc_diagram(X, X.faces[0], 1)
proj, imm = fold_complex_morphism(f)

resolutions = resolve_free_faces(imm, max_depth = 100, max_resolutions = 1000)
max_verts = -1
all_sat = True
for resolution in resolutions:
	verts = len(resolution.domain.G.vertices)
	sat_npi = valid_npis(resolution.domain)
	print(f'Sat. NPI: {sat_npi} # Vert: {verts}')
	max_verts = max(max_verts, verts)
	all_sat = all_sat and sat_npi
	#resolution.f.visualize()

print(f'Max Verts: {max_verts}')
print(f'All Sat: {all_sat}')

'''
children = get_children(X, imm)
#child = next(filter(lambda child: len(child.domain.G.vertices) == 3, children))

#children = get_children(X, child)

for child in children:
	print(child.domain)
	print(f'Chi: {child.domain.chi()}')
	print(f'Is Immersion: {child.is_immersion()}')
	print('---------------')
	child.f.visualize()
'''