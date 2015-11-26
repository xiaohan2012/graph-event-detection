import numpy as np


def sample_nodes(g, node_sample_size=100):
    nodes = g.nodes()
    return [nodes[i]
            for i in np.random.permutation(len(g.nodes()))[:node_sample_size]]
