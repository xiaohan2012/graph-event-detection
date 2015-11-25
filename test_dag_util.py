import networkx as nx
from .dag_util import binarize_dag, is_binary, unbinarize_dag
from .enron_graph import EnronUtil
from nose.tools import assert_equal, assert_true
import random

def _get_example_dag():
    # When create structure
    g = nx.DiGraph()
    g.add_nodes_from(range(1, 13))
    g.add_edges_from([(1, 2), (1, 3), (1, 7),
                      (2, 4), (2, 5), (2, 6),
                      (2, 7), (3, 8), (3, 9),
                      (5, 10), (5, 11), (7, 12),
                      (8, 12), (2, 8)])
    # When add weights
    for n in g.nodes():
        g.node[n][EnronUtil.VERTEX_REWARD_KEY] = 1
    g.node[2][EnronUtil.VERTEX_REWARD_KEY] = 11  # some special treatment

    for s, t in g.edges():
        g[s][t][EnronUtil.EDGE_COST_KEY] = 1
    g[1][2][EnronUtil.EDGE_COST_KEY] = 10  # some special treatment
    
    # add some time to nodes
    for n in g.nodes():
        g.node[n]['datetime'] = random.random()

    return g


def test_binarize_dag():
    g = _get_example_dag()
    
    # It should...
    binary_g = binarize_dag(g,
                            vertex_weight_key=EnronUtil.VERTEX_REWARD_KEY,
                            edge_weight_key=EnronUtil.EDGE_COST_KEY,
                            dummy_node_name_prefix='d_')
    expected_nodes = range(1, 13) + ['d_{}'.format(i) for i in range(1, 5)]
    assert_equal(
        sorted(expected_nodes),
        sorted(binary_g.nodes())
    )
    
    expected_edges = [(1, 'd_1'), (1, 7), ('d_1', 2),
                      ('d_1', 3), (3, 8), (3, 9),
                      (2, 'd_2'), (2, 'd_4'),
                      ('d_4', 'd_3'), ('d_4', 7),
                      ('d_2', 4), ('d_2', 8),
                      ('d_3', 6), ('d_3', 5),
                      (7, 12), (8, 12),
                      (5, 10), (5, 11)]
    assert_equal(
        sorted(expected_edges),
        sorted(binary_g.edges())
    )
    
    node_rewards = [1, 11] + [1] * 10 + [0] * 4
    for r, n in zip(node_rewards, expected_nodes):
        assert_equal(r, binary_g.node[n][EnronUtil.VERTEX_REWARD_KEY])

    edge_costs = [0, 1, 10,
                  1, 1, 1,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 1,
                  1, 1,
                  1, 1]
    for c, (s, t) in zip(edge_costs, expected_edges):
        assert_equal(c, binary_g[s][t][EnronUtil.EDGE_COST_KEY])
        
    assert_true(is_binary(binary_g))

    # check `dummy` attribute is ON for dummy nodes
    for n in g.nodes():
        if isinstance(n, basestring) and n.startswith('d_'):
            assert_true(g.node[n].get('dummy'))
            p = g.in_edges(n)[0]
            assert_equal(g.node[n]['datetime'], g.node[p]['datetime'])


def test_unbinarize_dag():
    g1 = _get_example_dag()
    binary_g = binarize_dag(g1,
                            vertex_weight_key=EnronUtil.VERTEX_REWARD_KEY,
                            edge_weight_key=EnronUtil.EDGE_COST_KEY,
                            dummy_node_name_prefix='d_')
    g2 = unbinarize_dag(binary_g,
                        edge_weight_key=EnronUtil.EDGE_COST_KEY,
    )
    assert_equal(sorted(g1.nodes()), sorted(g2.nodes()))
    assert_equal(sorted(g1.edges()), sorted(g2.edges()))
    match_func = lambda a1, a2: a1.items() == a2.items()
    assert_true(nx.is_isomorphic(g1, g2,
                                 node_match=match_func,
                                 edge_match=match_func))
    
