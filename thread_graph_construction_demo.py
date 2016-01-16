import networkx as nx


a, b, c = 'a', 'b', 'c'

# high density graph
g1 = nx.DiGraph()

g1.add_edges_from([(a, 1), (1, b), (1, c),
                   (b, 2), (2, a), (2, c),
                   (c, 3), (3, b), (3, a)])
print(nx.pagerank(g1))

# medium density graph
g2 = nx.DiGraph()

g2.add_edges_from([(a, 1), (1, b),
                   (b, 2), (2, a),
                   (c, 3), (3, b), (3, a)])
print(nx.pagerank(g2))

# low density graph
g3 = nx.DiGraph()

g3.add_edges_from([(a, 1),
                   (b, 2), (2, a),
                   (c, 3), (3, b)  # c @b
               ])
print(nx.pagerank(g3))
