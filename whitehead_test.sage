from whitehead import *
from grouppair import *

import random
def random_auto(autos):
	n = random.randrange(len(autos))
	return prod(map(lambda _: random.choice(autos), range(n)))


F.<a, b> = FreeGroup()
type1, type2 = whitehead_automorphisms(F)
autos = (type1, type2)
total_autos = type1 + type2


GP1 = GroupPair(F, [a*b^3, a*b*a])
phi = random_auto(total_autos)
GP2 = GP1.apply(phi)

psi = GP1.isomorphism(GP2)
print(psi)