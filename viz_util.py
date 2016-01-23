def to_d3_graph(g):
    """convert networkx format graph to d3 format
    node/edge attributes are copied
    """
    data = {'nodes': [], 'edges': []}
    for n in g.nodes_iter():
        node = g.node[n]
        for f in ('topics', 'bow', 'hashtag_bow'):
            if f in node:
                del node[f]

        node['name'] = n
        data['nodes'].append(node)

    name2index = {n: i
                  for i, n in enumerate(g.nodes_iter())}

    for s, t in g.edges_iter():
        edge = g[s][t]
        edge['source'] = name2index[s]
        edge['target'] = name2index[t]
        data['edges'].append(edge)

    return data


def add_subgraph_specific_attributes_to_graph(
        mother_graph,
        children_graphs_with_attrs):
    """
    merge sub graphs into mother graph
    and add sub graph specific attributes to
    both nodes and edges in the sub graph

    for each children, it should be a subgraph of mother_g
    children_graphs_with_attrs: list of tuples of (graph, dict)
    """
    for sub_g, attrs in children_graphs_with_attrs:
        for n in sub_g.nodes_iter():
            assert n in mother_graph, '{} not in mother graph'.format(n)
            mother_graph.node[n].update(attrs)
        for s, t in sub_g.edges_iter():
            assert mother_graph.has_edge(s, t)
            mother_graph[s][t].update(attrs)

    return mother_graph
