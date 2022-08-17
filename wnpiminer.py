from labels import *
from face import *
from complex import Complex, Morphism as ComplexMorphism
from graph import Graph, Morphism as GraphMorphism
from facialtree import *
from folding import fold_complex_morphism
from presentation import Presentation
import sys, time, random, json, os

def check_wnpi(imm, filename = None):
	if imm.domain.chi() > 1:
		if filename == None:
			filename = f'counterexamples/weak-ex{random.randint(0, 100)}-{int(time.time())}.json'
		with open(filename, 'w') as f:
			f.write(json.dumps(imm.json()))
			print('Weak NPI Counterexample Found')
		sys.exit(0)

# Generate all words in a,b of length `length` with exponent sum m in b
def word_sum_generator(length, m, reduced = False, prev_letter = ('', 0)):
	if length == 0 and m == 0:
		yield ''

	if length < abs(m):
		return

	skip = (prev_letter[0], -1*prev_letter[1])
	for g in ['a', 'b']:		
		for p in [1, -1]:
			if reduced and (g, p) == skip:
				continue
			for w in word_sum_generator(length - 1, m - (p if g == 'b' else 0), reduced = reduced, prev_letter = (g, p)):
				G = g.upper() if p == -1 else g
				yield G + w

def cyclically_reduced_word_sum(length, m):
	for w in word_sum_generator(length, m, reduced = True):
		if len(w) >= 2:
			start = w[0]
			end = w[-1]
			if start != end and start.lower() == end.lower():
				continue
		yield w

def cyclically_equal(w1, w2):
	if len(w1) != len(w2):
		return False
	for i in range(len(w1)):
		if w1[i:] + w1[:i] == w2:
			return True
	return False

def unique_up_to_cycling(length, m):
	seen = []
	for w in cyclically_reduced_word_sum(length, m):
		unique = True
		for ww in seen:
			if cyclically_equal(w, ww):
				unique = False
				break
		if not unique:
			continue
		seen.append(w)
		yield w

def traverse(data):
	X, depth, filename = data

	eps = random.randrange(len(X.faces))
	f = Complex.disc_diagram(X, X.faces[eps], 1)
	proj, imm = fold_complex_morphism(f)

	parent = imm
	for d in range(depth):
		try:
			children = get_children(X, parent, check_npi = lambda g: check_wnpi(g, filename = filename))
		except SystemExit:
			return True

		parent = random.choice(children)

	return False

if __name__ == '__main__':
	import itertools

	n = 1
	depth = 10
	max_iters = 30
	# Use multiprocessing
	import multiprocessing as mp

	for length in range(6, 7):
		for w in unique_up_to_cycling(length, 1):
			if w not in ['AbAbAB']:
				continue

			P = Presentation.from_strings(['a', 'b'], [w, 'b' + 'a'*n + 'B' + 'A'*(n + 1)])
			X = P.complex()

			print(f'On word {w}...')
			filename = f'counterexamples/weak-w={w}-n={n}.json'

			pool = mp.Pool(mp.cpu_count() - 1)
			for found in tqdm(pool.imap_unordered(traverse, itertools.repeat((X, depth, filename), max_iters)), total = max_iters):
				if found:
					pool.terminate()
					break
			pool.close()