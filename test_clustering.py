import networkx as nx

from nose.tools import assert_equal

from .clustering import greedy_clustering_on_graph, string_similar_probability


def test_greedy_clustering_on_graph():
    g = nx.DiGraph()
    g.add_nodes_from(
        [('1-a', {'body': 'pig on a lip stick'}),
         ('1-b', {'body': 'Pig on a Lip stick'}),
         ('2-a', {'body': 'helsinki day'}),
         ('2-b', {'body': 'helsinki day1'}),
         ('3-a', {'body': 'different'})]
    )
    for n in g.nodes_iter():
        g.node[n]['subject'] = ''

    g.add_path(['1-a', '1-b', '2-a', '2-b', '3-a'])

    actual = greedy_clustering_on_graph(
        g,
        metric=string_similar_probability,
        threshold=0.8
    )
    assert_equal(
        {
            '1-a': 0,
            '1-b': 0,
            '2-a': 1,
            '2-b': 1,
            '3-a': 2
        },
        actual
    )
