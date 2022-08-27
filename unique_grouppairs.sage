from grouppair import *
from wnpiminer import unique_up_to_cycling

def str_to_word(word, F):
	gens = {str(g) : g for g in F.gens()}
	word = [gens[c.lower()]^(-1 if c.isupper() else 1) for c in word]
	return prod(word)

max_length = 6

F.<a, b> = FreeGroup()
words = sum(map(lambda i: list(unique_up_to_cycling(i, 1)), range(1, max_length + 1)), [])
words = [str_to_word(w, F) for w in words]

grouppairs = [GroupPair(F, [w, b*a*b^-1*a^-2]) for w in words]

classes = []
from tqdm import tqdm
for gp in tqdm(grouppairs):
	seen = False
	for clas in classes:
		rep = clas[0]
		if rep.is_isomorphic(gp):
			clas.append(gp)
			seen = True
			break
	if not seen:
		classes.append([gp])

orig = [[gp.ws[0].gen for gp in clas] for clas in classes]
print(orig)

'''
[[b, a*b, a^-1*b, a^2*b, a^-2*b, a^3*b, a^-3*b, a^4*b, a^-4*b, a^5*b, a^-5*b],
 [a*b^2*a*b^-1, (a*b)^2*a*b^-1, a*b*a^-1*b*a*b^-1],
 [a*b^2*a^-1*b^-1, (a*b)^2*a^-1*b^-1, a*(b*a^-1)^2*b^-1],
 [a*b^-1*a^-1*b^2, a*b*a*b^-1*a^-1*b],
 [a^-1*b^2*a^-1*b^-1, a*b*a^-1*b^-1*a^-1*b, (a^-1*b)^2*a^-1*b^-1],
 [a^2*b^2*a*b^-1],
 [a^2*b^2*a^-1*b^-1],
 [a^2*b^-1*a*b^2],
 [a^2*b^-1*a^-1*b^2],
 [a*b^2*a^-2*b^-1],
 [a*b^-1*a^-2*b^2],
 [a*b^-1*(a^-1*b)^2],
 [a^-2*b^2*a^-1*b^-1],
 [a^-2*b^-1*a^-1*b^2]]
 '''