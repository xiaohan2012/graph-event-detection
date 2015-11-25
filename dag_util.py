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
                 dummy_node_name_prefix='d_'):
    g = g.copy()  # be functional
    dummy_node_counter = 1
    for u in nx.topological_sort(g):
        nbs = g.neighbors(u)
        while len(nbs) > 2:
            for p_1, p_2 in chunks(nbs, 2):
                v = "{}{}".format(
                    dummy_node_name_prefix,
                    dummy_node_counter
                )
                g.add_node(v)
                g.node[v]['dummy'] = True
                print(g.node[u])
                g.node[v]['datetime'] = g.node[u]['datetime']
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


def unbinarize_dag(g,
                   edge_weight_key):
    """
    convert binarized dag back to the original dag
    """
    g = g.copy()  # be functional
    for v in nx.topological_sort(g):
        print(v, g.node[v])
        if g.node[v].get('dummy'):
            parents = g.in_edges(v)
            assert len(parents) == 1
            u = parents[0][0]
            for c in g.neighbors(v):
                g.add_edge(u, c)
                g[u][c][edge_weight_key] = g[v][c][edge_weight_key]
            g.remove_node(v)
    return g


def is_binary(g):
    """check if the DAG is binary
    """
    for n in g.nodes():
        if len(g.neighbors(n)) > 2:
            return False
    return True
