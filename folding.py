import itertools
from graph import Graph
from graph import Morphism as GraphMorphism
from setfunction import SetFunction
from face import Face
from complex import FaceMap, Complex
from complex import Morphism as ComplexMorphism
from labels import *

'''
	Returns the folded decomposition A -> C, C -> B of the complex morphism f : A -> B
	Rational curvature invariants for 2-complexes (Lemma 2.6)
'''
def fold_complex_morphism(f):
	A = f.domain
	B = f.codomain

	proj, g = fold_graph_morphism(f.f)
	C_skeleton = g.domain

	vertex_to_indice = {}
	C_faces = []
	C_B_face_maps = {}
	A_C_face_maps = {}
	vertices = set()
	edges = set()
	for face, fm in f.face_maps.items():
		ind = 0
		C_face = []
		for i in range(len(face)):
			Y_fold_im = proj.f_E[face[i]]

			initial_vertex = (Y_fold_im.initial, (fm.target, fm.initial(i)))
			terminal_vertex = (Y_fold_im.terminal, (fm.target, fm.terminal(i)))
			# Already accounted for this cycle in the image, or have reached start
			if initial_vertex in vertices:
				break

			e = Edge(initial_vertex, terminal_vertex)
			if initial_vertex not in vertex_to_indice:
				vertex_to_indice[initial_vertex] = (ind, len(C_faces), fm.orientation)
				ind += 1

			C_face.append(Y_fold_im)

			edges.add(e)

			# Only add initial vertex at each step
			vertices.add(initial_vertex)

		if C_face != []:
			C_face = Face(C_face)
			C_faces.append(C_face)
			C_B_face_maps[C_face] = FaceMap(C_face, fm.target, fm.start_index, fm.orientation, origin_start_index = fm.origin_start_index)

		# Populate projection face
		Y_fold_im = proj.f_E[face[0]]

		# This is very scuffed way to determine A -> C face maps
		initial_vertex = (Y_fold_im.initial, (fm.target, fm.initial(0)))
		ind, f_ind, orient = vertex_to_indice[initial_vertex]
		
		A_C_face_maps[face] = FaceMap(face, C_faces[f_ind], ind, fm.orientation * orient)

	C_B_face_maps = SetFunction(C_B_face_maps)
	A_C_face_maps = SetFunction(A_C_face_maps)

	C = Complex(C_skeleton, C_faces)

	imm = ComplexMorphism(C, B, g, C_B_face_maps)
	proj = ComplexMorphism(A, C, proj, A_C_face_maps)

	return proj, imm


'''
	Returns the decomposition G -> G_fold, G_fold -> H of the graph morphism f : G -> H
'''
def fold_graph_morphism(f):
	proj = GraphMorphism.identity(f.domain)
	while True:
		folded = False

		G = f.domain
		for v in G.vertices:
			for e1, e2 in itertools.product(G.neighborhood(v), repeat = 2):
				if e1 == e2:
					continue
				if f.f_E[e1] == f.f_E[e2]:
					folded = True
					_proj, f = fold_admissible_pair(f, e1, e2)
					proj = GraphMorphism.compose(_proj, proj)
					break
			if folded:
				break

		if not folded:
			break

	return proj, f

'''
	Returns the factoring of f through G/[e1 = e2]
'''
def fold_admissible_pair(f, e1, e2):
	G = f.domain
	proj = fold_admissible_pair_graph(G, e1, e2)
	G_fold = proj.codomain
	g_V = SetFunction()
	g_E = SetFunction()
	for v in G.vertices:
		g_V[proj.f_V[v]] = f.f_V[v]
	for e in G.edges:
		g_E[proj.f_E[e]] = f.f_E[e]

	g = GraphMorphism(G_fold, f.codomain, g_V, g_E)

	# Sanity check
	#assert GraphMorphism.compose(g, proj) == f

	return proj, g


'''
	Folds a graph along an admissible pair and returns the canonical map G -> G/[e1 = e2]
'''
def fold_admissible_pair_graph(G, e1, e2):
	if e1.initial != e2.initial:
		raise Exception('Can only fold edges which share an initial vertex.')

	v = e1.terminal
	w = e2.terminal

	Gp, newV, newE = G.copy(include_maps = True)
	for e in G.orientation:
		newE[G.bar(e)] = Gp.bar(newE[e])

	vp = newV[v]
	wp = newV[w]

	e1p = newE[e1]
	e2p = newE[e2]
	if wp != vp:
		Gp.remove_vertex(wp, remove_edges = False)
	Gp.remove_edge(e2p)

	if wp != vp:
		for e in Gp.edges:
			if e.terminal == wp:
				e.terminal = vp
			if e.initial == wp:
				e.initial = vp

	f_V = SetFunction(newV)
	f_E = SetFunction(newE)
	f_V[w] = vp
	f_E[e2] = e1p
	f_E[G.bar(e2)] = Gp.bar(e1p)

	return GraphMorphism(G, Gp, f_V, f_E)
