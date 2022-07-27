from facialtree import *
import itertools

def order_preserve_remove_duplicates(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]

'''
	Tries to resolve a free face in the domain of an immersion.
'''
def resolve_free_face(f, e, embed_free_faces = []):
	# Isn't a free face
	if not f.domain.is_free_face(e):
		return f

	vertex = e.initial
	X = f.codomain

	children = get_children_at_vertex(X, f, vertex, include_maps = True)

	resolutions = []
	for imm, proj in children:
		if not imm.domain.is_free_face(proj.f.f_E[e]):
			new_edges = [imm.domain.G.oriented(proj.f.f_E[ee]) for ee in embed_free_faces if imm.domain.is_free_face(proj.f.f_E[ee])]
			resolutions.append((imm, new_edges))

	return resolutions

def resolve_free_faces(f, max_depth = 10, max_resolutions = 100):
	# Resolve earliest free face stuff first
	to_resolve = [(f, f.domain.free_faces(edges_only = True))]
	num_resolutions = 0
	resolutions = []
	#while num_resolutions < max_resolutions and len(to_resolve) > 0:
	from tqdm import tqdm
	for d in tqdm(range(max_depth)):
		new_to_resolve = []
		for j in range(len(to_resolve) - 1, -1, -1):
			if len(resolutions) >= max_resolutions:
				break

			g, free_faces = to_resolve.pop(j)
			if len(free_faces) == 0:
				resolutions.append(g)
				# use break to get larger ones in computation time
				continue
			e = free_faces.pop(0)

			# Do it this way to resolve the earliest arising free faces first
			g_resolutions = resolve_free_face(g, e, embed_free_faces = free_faces)
			for i, v in enumerate(g_resolutions):
				resol, embedded = v
				new_free = resol.domain.free_faces(edges_only = True)
				embedded = order_preserve_remove_duplicates(embedded + new_free)
				g_resolutions[i] = (resol, embedded)

			num_resolutions += 1
			new_to_resolve += g_resolutions

		if len(resolutions) >= max_resolutions:
			break

		to_resolve = new_to_resolve
		if len(to_resolve) == 0:
			break

	if len(to_resolve) > 0:
		print('Failed to resolve all free faces with computation bounds.')
	return resolutions