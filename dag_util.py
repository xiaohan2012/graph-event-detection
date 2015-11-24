import networkx as nx


def chunks(lst, chunk_size):
    """if the last chunk's size is smaller than chunk_size, then it's not returned
    """
    for i in xrange(0, len(lst), chunk_size):
        if i + chunk_size > len(lst):
            break
        yield lst[i: i + chunk_size]


def binarize_dag(g,
                 vertex_weight_key,
                 edge_weight_key,
                 dummy_node_name_prefix='d'):
    g = g.copy()  # be functional
    dummy_node_counter = 1
    for u in nx.topological_sort(g):
        nbs = g.neighbors(u)
        while len(nbs) > 2:
            print(list(chunks(nbs, 2)))
            for p_1, p_2 in chunks(nbs, 2):
                v = "{}{}".format(
                    dummy_node_name_prefix,
                    dummy_node_counter
                )
                g.add_node(v)
                g.add_edge(u, v)
                g.add_edges_from([(v, p_1),
                                  (v, p_2)])

                g.node[v][vertex_weight_key] = 0
                g[v][p_1][edge_weight_key] = g[u][p_1][edge_weight_key]
                g[v][p_2][edge_weight_key] = g[u][p_2][edge_weight_key]
                g[u][v][edge_weight_key] = 0
                
                g.remove_edges_from([(u, p_1), (u, p_2)])
                dummy_node_counter += 1
            nbs = g.neighbors(u)
    return g
            

def is_binary(g):
    """check if the DAG is binary
    """
    for n in g.nodes():
        if len(g.neighbors(n)) > 2:
            return False
    return True
