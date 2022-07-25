import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz
import os
import tempfile


class GraphVisualization:
    def __init__(self):
        self.G = nx.MultiDiGraph()

    @staticmethod
    def from_graph(G, edge_labels = {}, vertex_labels = {}):
        visual = GraphVisualization()
        vertices = {v:i for i,v in enumerate(G.vertices)}
        for v, i in vertices.items():
            visual.G.add_node(i, label = vertex_labels.get(v, v.label))

        for e in G.orientation:
            visual.G.add_edge(vertices[e.initial], vertices[e.terminal], label = edge_labels.get(e, e.label))

        return visual

    def visualize(self):
        ag = nx.nx_agraph.to_agraph(self.G)
        GraphVisualization.style(ag)
        ag.layout(prog="dot")
        temp = tempfile.NamedTemporaryFile(delete = False)
        tempname = temp.name + ".png"
        ag.draw(tempname)
        img = mpimg.imread(tempname)
        plt.axis('off')
        plt.imshow(img)
        plt.show()
        os.remove(tempname)

    @staticmethod
    def style(G):
        G.node_attr['shape'] = 'circle'