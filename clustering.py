import networkx as nx
from difflib import SequenceMatcher


def string_similar_probability(a, b):
    return SequenceMatcher(None, a, b).ratio()


def greedy_clustering_on_graph(
        g,
        metric=string_similar_probability,
        threshold=0.8):
    def get_text(n):
        return u'{} {}'.format(
            g.node[n]['subject'], g.node[n]['body']
        )
    cluster_assignment = {}
    node_pool = list(nx.topological_sort(g))
    cluster_count = -1
    while len(node_pool) > 0:
        cluster_count += 1
        node = node_pool.pop(0)
        cluster_assignment[node] = cluster_count

        not_similar_nodes = filter(
            lambda n: metric(get_text(node), get_text(n)) < threshold,
            node_pool
        )
        similar_nodes = set(node_pool) - set(not_similar_nodes)
        for n in similar_nodes:
            cluster_assignment[n] = cluster_count
        node_pool = not_similar_nodes
    return cluster_assignment
