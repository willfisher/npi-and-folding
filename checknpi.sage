import time, json, random, sys

def pres_to_sage(pres):
	G = FreeGroup(len(pres.generators))
	rels = [G([i*(pres.generators.index(g) + 1) for g, i in rel]) for rel in pres.relations]
	H = G/rels
	return H

def is_trivial(H):
	if len(H.abelian_invariants()) > 0:
		return False
	return H.cardinality(limit = 100000) == 1

def is_indicable(H):
	abelian_invariants = H.abelian_invariants()
	indicable = 0 in abelian_invariants
	return indicable

def trivial_indicable(H):
	abelian_invariants = H.abelian_invariants()
	indicable = 0 in abelian_invariants
	if len(abelian_invariants) == 0:
		trivial = H.cardinality(limit = 100000) == 1
	else:
		trivial = False

	return trivial, indicable

def check_wnpi(imm, filename = None):
	if imm.domain.chi() > 1:
		if filename == None:
			filename = f'counterexamples/normal-ex{random.randint(0, 100)}-{int(time.time())}.json'
		with open(filename, 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Normal NPI Counterexample Found')
			sys.exit(0)


def check_npis(imm):
	Y = imm.domain

	pres = pres_to_sage(Y.presentation())
	trivial, indicable = trivial_indicable(pres)
	if trivial:
		indicable = True
		G = FreeGroup(pres.generators())
		r = pres.relations()
		for i in range(len(r)):
			H = G/(r[:i] + r[i + 1:])
			indicable = indicable & is_indicable(H)

	if (not indicable) or (Y.chi() > 0 and not trivial):
		with open(f'counterexamples/normal-ex{random.randint(0, 100)}-{int(time.time())}.json', 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Normal NPI Counterexample Found')
			sys.exit(0)
	elif Y.chi() > 1:
		with open(f'counterexamples/weak-ex{random.randint(0, 100)}-{int(time.time())}.json', 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Weak NPI Counterexample Found')
			sys.exit(0)
