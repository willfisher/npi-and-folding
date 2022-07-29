from complex import Complex, Morphism as ComplexMorphism
from folding import fold_complex_morphism
import itertools
from tqdm import tqdm

'''
	Optionally include maps to give the canonical map parent -> child
'''
def get_children(X, piece, include_maps = False):
	vertices = piece.domain.G.vertices
	image_sorted = image_sort(vertices, piece.f.f_V)
	piece_im = set(image_sorted.keys())

	children = []
	for face, orientation in tqdm(itertools.product(X.faces, [1, -1]), total = len(X.faces)*2):
		f = Complex.disc_diagram(X, face, orientation)
		disc_image_sorted = image_sort(f.domain.G.vertices, f.f.f_V)
		shared = set(disc_image_sorted.keys()).intersection(piece_im)
		for im in shared:
			for v1, v2 in itertools.product(image_sorted[im], disc_image_sorted[im]):
				data = wedged_fold(piece, v1, f, v2, include_maps = include_maps)
				imm = data if not include_maps else data[0]

				if imm.domain.chi() > 1:
					import json, time
					with open(f'counterexamples/ex{int(time.time())}.json', 'wb') as f:
						f.write(json.dumps(imm.json()))

				# Is facial strict
				if len(imm.domain.faces) == len(piece.domain.faces) + 1:
					children.append(data)

	return children

def get_children_at_vertex(X, piece, v, include_maps = False):
	children = []
	for face, orientation in itertools.product(X.faces, [1, -1]):
		f = Complex.disc_diagram(X, face, orientation)
		disc_image_sorted = image_sort(f.domain.G.vertices, f.f.f_V)
		for v2 in disc_image_sorted.get(piece.f.f_V[v], []):
			data = wedged_fold(piece, v, f, v2, include_maps = include_maps)
			imm = data if not include_maps else data[0]
			
			# Not facial strict
			children.append(data)

	return children

def wedged_fold(f1, v1, f2, v2, include_maps = False):
	g, incl, _ = ComplexMorphism.wedge(f1, v1, f2, v2, include_maps = True)
	proj, imm = fold_complex_morphism(g)
	
	data = imm
	if include_maps:
		proj = ComplexMorphism.compose(proj, incl)
		data = imm, proj
	
	return data

def image_sort(domain, func):
	image_sorted = {}
	for v in domain:
		im = func[v]
		if im not in image_sorted:
			image_sorted[im] = []
		image_sorted[im].append(v)

	return image_sorted