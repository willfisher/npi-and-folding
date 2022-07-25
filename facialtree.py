from complex import Complex, Morphism as ComplexMorphism
from folding import fold_complex_morphism
import itertools

def get_children(X, piece):
	vertices = piece.domain.G.vertices
	image_sorted = image_sort(vertices, piece.f.f_V)
	piece_im = set(image_sorted.keys())

	children = []
	for face in X.faces:
		f = Complex.disc_diagram(X, face)
		disc_image_sorted = image_sort(f.domain.G.vertices, f.f.f_V)
		shared = set(disc_image_sorted.keys()).intersection(piece_im)
		for im in shared:
			for v1, v2 in itertools.product(image_sorted[im], disc_image_sorted[im]):
				g = ComplexMorphism.wedge(piece, v1, f, v2)
				proj, imm = fold_complex_morphism(g)
				if len(imm.domain.faces) == len(piece.domain.faces) + 1:
					children.append(imm)

	return children



def image_sort(domain, func):
	image_sorted = {}
	for v in domain:
		im = func[v]
		if im not in image_sorted:
			image_sorted[im] = []
		image_sorted[im].append(v)

	return image_sorted