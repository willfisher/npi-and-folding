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

def check_npis(imm):
	Y = imm.domain
	if Y.chi() <= 0:
		return

	if not is_trivial(pres_to_sage(Y.presentation())):
		with open(f'counterexamples/strong-ex{random.randint(0, 100)}-{int(time.time())}.json', 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Normal NPI Counterexample Found')
			sys.exit(0)
	elif Y.chi() > 1:
		with open(f'counterexamples/weak-ex{random.randint(0, 100)}-{int(time.time())}.json', 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Weak NPI Counterexample Found')
			sys.exit(0)
