import itertools
from graph import Graph
from graph import Morphism as GraphMorphism
from setfunction import SetFunction
from face import Face
from complex import FaceMap, Complex
from complex import Morphism as ComplexMorphism

'''
	Returns the folded decomposition A -> C, C -> B of the complex morphism f : A -> B
	Rational curvature invariants for 2-complexes (Lemma 2.6)
'''
def fold_complex_morphism(f):
	A = f.domain
	B = f.codomain

	proj, g = fold_graph_morphism(f.f)
	C_skeleton = g.domain

	A_C_face_maps = SetFunction()
	C_B_face_maps = SetFunction()
	seen = {}
	for face, fm in f.face_maps.items():
		fm_face = Face([(proj.f_E[face[i]], (fm.target, fm[i])) for i in range(len(face))])
		fm_offset = 0
		fm_orientation = 1
		C_face = None
		for k,v in seen.items():
			offset, orientation = Face.offset_equal(fm_face, k)
			if offset >= 0:
				C_face = v
				fm_offset = offset
				fm_orientation = orientation
				break
		
		if C_face == None:
			C_face = Face([e[0] for e in fm_face])
			seen[fm_face] = C_face
			C_B_face_maps[C_face] = FaceMap(C_face, fm.target, fm.start_index, fm.orientation)
		
		A_C_face_maps[face] = FaceMap(face, C_face, fm_offset, fm_orientation)

	C_faces = list(C_B_face_maps.keys())
	C = Complex(C_skeleton, C_faces)

	imm = ComplexMorphism(C, B, g, C_B_face_maps)
	proj = ComplexMorphism(A, C, proj, A_C_face_maps)

	return proj, imm

''' THIS IS AN OLD IMPLEMENTATION BASED OFF A MISUNDERSTANDING
	Returns the folded decomposition A -> C, C -> B of the complex morphism f : A -> B
	Rational curvature invariants for 2-complexes (Lemma 2.6)
def fold_complex_morphism(f):
	A = f.domain
	B = f.codomain

	proj, g = fold_graph_morphism(f.f)
	C_skeleton = g.domain

	# Push faces from A forwards to C
	C_face_maps = {}
	target_sorted = {}
	Orig_to_C = {}
	for face, fm in f.face_maps.items():
		C_face = Face([proj.f_E[e] for e in face.face])
		face_map = FaceMap(C_face, fm.target, fm.start_index, fm.orientation)
		C_face_maps[C_face] = face_map

		Orig_to_C[face] = C_face

		if fm.target not in target_sorted:
			target_sorted[fm.target] = []
		target_sorted[fm.target].append(C_face)

	# Prune faces mapping to the same face in B and having the same attaching map
	C_faces = []
	# Keep track of collapsed faces
	collapsed = {}
	for preimage in target_sorted.values():
		i = 0
		while i < len(preimage):
			f1 = preimage[i]
			for j in range(len(preimage) - 1, i, -1):
				f2 = preimage[j]
				offset = Face.offset_equal(f2, f1)
				if offset >= 0:
					collapsed[f2] = (f1, offset)
					del preimage[j]

			i += 1

		C_faces += preimage

	C_face_maps = SetFunction({f:C_face_maps[f] for f in C_faces})
	C = Complex(C_skeleton, C_faces)

	# Construct the folded immersion
	imm = ComplexMorphism(C, B, g, C_face_maps)

	# Construct projection onto folded representative
	A_face_maps = SetFunction()
	for face in A.faces:
		if face in collapsed:
			facep, offset = collapsed[face]
			target = Orig_to_C[facep]
		else:
			target = Orig_to_C[face]
			offset = 0
		fm = FaceMap(face, target, offset, 1)
		A_face_maps[face] = fm

	proj = ComplexMorphism(A, C, proj, A_face_maps)

	return proj, imm
'''



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
