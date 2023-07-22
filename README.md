# NPI and Folding
This is a library for handling Stallings style foldings of graphs and 2-complexes. It was created to facilitate the algorithm described in [Contractible complexes and non-positive immersions](https://arxiv.org/abs/2210.02304) to produce contractible complexes with non-positive immersions.

Alongside computing foldings of complexes, this library also has the ability to determine when two presentations are Nielsen equivalent.

## How to Use
### Graphs
Graphs may be constructed using the `Graph` class by providing an array of vertices and an array of edges. For example, the cyclic graph on `n` vertices may be constructed with
```python
from graph import Graph
from labels import Edge, Vertex

n = 5
vertices = [Vertex(i) for i in range(n)]
graph = Graph(vertices, [Edge(vertices[i], vertices[(i + 1) % n]) for i in range(n)])
```
Morphisms of graphs are represented by the `GraphMorphism` class which is constructed by provided the source and target graphs, as well as maps representing the induced maps on vertices and edges.

### 2-complexes
#### From cellular decomposition
A 2-complex can be constructed by providing the graph of the 1-skeleton and an array of faces representing the 2-cells of the complex. A face, or 2-cell, is represented by the `Face` class, which is constructed by an array of edges occurring in the boundary of the face when traversed clockwise or counter-clockwise starting at any vertex.

Using the example of the cyclic graph in [Graphs](#graphs), we may construct a 2-complex representing a single disc with boundary a cycle of length `n` as follows:
```python
from commongraphs import cycle

n = 5
# Construct cycle of length n for 1-skeleton
C = cycle(n)

C_face = []
# Pick a random edge in C
curr = next(iter(C.orientation))
# Traverse the cycle, appending the edges as they occur to the 2-cell 
for i in range(n):
	C_face.append(curr)
	curr = next(iter(C.out_edges(curr.terminal)))
# Construct the Face object
C_face = Face(C_face)

# Create a disc with C as the 1-skeleton and C_face the only 2-cell
D = Complex(C, [C_face])
```

#### From presentation
The presentation complex of a group presentation may also be conveniently constructed. For doing this, see [Presentations](#presentations).

#### Visualization
Using the `pygraphviz` package, 2-complexes may be visualized using the `.visualize()` method.

### Presentations
Presentations may be constructed using the `Presentation` class. This may be most conveniently constructed using the `from_string` method which constructs a presentation from a string representation of the generators and relators.

For example, the presentation $\langle a,b | aba^{-1}b^{-1} \rangle$ may be constructed using:
```python
from presentation import Presentation

P = Presentation.from_strings(['a', 'b'], ['abAB'])
```
Note that generators should be represented by lowercase letters and relation strings are given as words with capitals denoting inverse.

Given a presentation object, the associated presentation complex may be constructed using `.complex()`. Thus we may alternatively construct the 2-complex associated to a disc with `n` vertices on its boundary via:
```python
from presentation import Presentation

n = 5
P = Presentation.from_strings(['a'], ['a'*n])
X = P.complex()
```

## Finding WNPI

The algorithm described in [Contractible complexes and non-positive immersions](https://arxiv.org/abs/2210.02304) to produce weak non-positive immersions is implemented in `wnpiminer.sage`.

## Requirements
This project uses SageMath for checking when complexes are contractible or when two presentations are Nielsen equivalent, but only Python for the basic functionality involving foldings and 2-complexes.