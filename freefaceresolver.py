from facialtree import *
import itertools

'''
	Tries to resolve a free face in the domain of an immersion.
'''
def resolve_free_face(f, e):
	# Isn't a free face
	if not f.domain.is_free_face(e):
		return f

	vertex = e.initial
	X = f.codomain

	children = get_children_at_vertex(X, f, vertex, include_maps = True)

	resolutions = []
	for imm, proj in children:
		if not imm.domain.is_free_face(proj.f.f_E[e]):
			resolutions.append(imm)

	return resolutions

def resolve_free_faces(f, max_resolutions = 100):
	to_resolve = [f]
	num_resolutions = 0
	resolutions = []
	while num_resolutions < max_resolutions and len(to_resolve) > 0:
		new_to_resolve = []
		for j in range(len(to_resolve) - 1, -1, -1):
			g = to_resolve.pop(j)
			free_faces = g.domain.free_faces()
			if len(free_faces) == 0:
				resolutions.append(g)
				break
			e = free_faces[0][0]
			g_resolutions = resolve_free_face(g, e)
			num_resolutions += 1
			new_to_resolve += g_resolutions

		to_resolve = new_to_resolve

	if len(to_resolve) > 0:
		print('Failed to resolve all free faces with computation bounds.')
	return resolutions