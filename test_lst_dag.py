from .lst import lst_dag
from nose.tools import assert_equal
from networkx.classes.digraph import DiGraph

from .dag_util import binarize_dag

def test_lst_dag():
    # input
    g = DiGraph()
    g.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])

    g.node[1]['r'] = 1
    g.node[2]['r'] = 1
    g.node[3]['r'] = 1.5
    g.node[4]['r'] = 1

    g[1][2]['c'] = 2
    g[1][3]['c'] = 1
    g[2][4]['c'] = 1
    g[3][4]['c'] = 3

    r = 1  # root
    U = range(6)  # 0...5

    # expected value
    one_node_tree = DiGraph()
    one_node_tree.add_node(1)
    expected_dags = [
        one_node_tree,
        DiGraph([(1, 3)]),
        DiGraph([(1, 3)]),  # DiGraph([(1, 2)])
        DiGraph([(1, 2), (1, 3)]),
        DiGraph([(1, 2), (1, 3), (2, 4)]),
        DiGraph([(1, 2), (1, 3), (2, 4)])
    ]

    for u, expected in zip(U, expected_dags):
        actual = lst_dag(g, r, u)
        print('u={}'.format(u))
        assert_equal(expected.edges(), actual.edges())


def _get_more_complicated_example_1():
    """get a binarized example, whose original graph is 
    more complicated than the above example
    """
    g = DiGraph()
    g.add_nodes_from(range(1, 10))
    g.add_edges_from([(1, 2), (1, 3), (1, 7),
                      (2, 4), (2, 5), (2, 6),
                      (2, 7), (3, 8), (3, 9)])
    rewards = range(1, 10)
    for r, n in zip(rewards, g.nodes()):
        g.node[n]['r'] = r
        
    # all edges have cost 2 except 1 -> 2 and 1 -> 3(cost 1)
    for s, t in g.edges():
        g[s][t]['c'] = 2
    g[1][2]['c'] = 1
    g[1][3]['c'] = 1
    
    return binarize_dag(g,
                        vertex_weight_key='r',
                        edge_weight_key='c',
                        dummy_node_name_prefix='d_')
    

def test_lst_dag_more_complicated_example():
    g = _get_more_complicated_example_1()
    U = [0, 2, 3, 4, 100]
    expected_edges_set = [
        [(1, 'd_1')],
        [(1, 7)],
        [(1, 'd_1'), ('d_1', 3), (3, 9)],
        [(1, 'd_1'), ('d_1', 3), (3, 9), ('d_1', 2), (2, 'd_2')],
        list(set(g.edges()) - set([(1, 7)]))
    ]

    for u, edges in zip(U, expected_edges_set):
        assert_equal(sorted(edges),
                     sorted(lst_dag(g, 1, u).edges()))
