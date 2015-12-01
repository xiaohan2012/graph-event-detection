import unittest
from nose.tools import assert_equal
from networkx.classes.digraph import DiGraph

from .lst import lst_dag, lst_dag_general
from .dag_util import binarize_dag


def get_example_1():
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

    U = range(6)  # 0...5
    
    expected_edge_list = [
        [],
        [(1, 3)],
        [(1, 3)],  # DiGraph([(1, 2)])
        [(1, 2), (1, 3)],
        [(1, 2), (1, 3), (2, 4)],
        [(1, 2), (1, 3), (2, 4)]
    ]
    return g, U, expected_edge_list


def get_example_2():
    # input
    g = DiGraph()
    g.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])
    
    g.node[1]['r'] = 1
    g.node[2]['r'] = 1
    g.node[3]['r'] = 1.5
    g.node[4]['r'] = 1
    
    g[1][2]['c'] = 0.021
    g[1][3]['c'] = 0.011
    g[2][4]['c'] = 0.009
    g[3][4]['c'] = 0.03

    U = [float(i) / 100 for i in xrange(6)]  # 0...5

    # expected value
    expected_edge_list = [
        [],
        [(1, 3)],
        [(1, 3)],
        [(1, 2), (1, 3)],
        [(1, 2), (1, 3), (2, 4)],
        [(1, 2), (1, 3), (2, 4)]
    ]

    return (g, U, expected_edge_list)


def get_example_3():
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
    
    g = binarize_dag(g,
                     vertex_weight_key='r',
                     edge_weight_key='c',
                     dummy_node_name_prefix='d_')
    
    # parameters and expected output
    U = [0, 2, 3, 4, 100]
    expected_edges_set = [
        [(1, 'd_1')],
        [(1, 7)],
        [(1, 'd_1'), ('d_1', 3), (3, 9)],
        [(1, 'd_1'), ('d_1', 3), (3, 9), ('d_1', 2), (2, 'd_2')],
        # (1, 7) removed to make it a tree
        list(set(g.edges()) - set([(1, 7)]))
    ]
    
    return (g, U, expected_edges_set)


class LstDagTestCase(unittest.TestCase):

    def test_lst_dag_example_1(self):
        g, U, expected_edge_list = get_example_1()
        r = 1
        for u, expected in zip(U, expected_edge_list):
            actual = lst_dag(g, r, u)
            assert_equal(sorted(expected),
                         sorted(actual.edges()))

    def test_lst_dag_example_2(self):
        """
        the case where edge weight are float
        """
        g, U, expected_edge_list = get_example_2()
        r = 1
        for u, expected in zip(U, expected_edge_list):
            actual = lst_dag(g, r, u,
                             edge_weight_decimal_point=2)
            print(actual.edges())
            assert_equal(expected, actual.edges())

    def test_lst_dag_example_3(self):
        g, U, expected_edges_set = get_example_3()
        for u, edges in zip(U, expected_edges_set):
            print(u)
            assert_equal(sorted(edges),
                         sorted(lst_dag(g, 1, u).edges()))


class LstDagGeneralTest(unittest.TestCase):
    def setUp(self):
        def local_cost_func(n, D, g, edge_cost_key,
                            decimal_point,
                            cost_child_tuples):
            if decimal_point:
                # TODO: unncessary re-computation
                multiplier = 10**decimal_point
            cost_sum = 0
            for cost, child in cost_child_tuples:
                cost_sum += cost
                if decimal_point:
                    cost_sum += int(round(
                        g[n][child][edge_cost_key] * multiplier
                    ))
                else:
                    cost_sum += g[n][child][edge_cost_key]
            return cost_sum
        self.local_cost_func = local_cost_func

    def test_lst_dag_local_example_1(self):
        g, U, expected_edges_set = get_example_1()
        for u, edges in zip(U, expected_edges_set):
            assert_equal(sorted(edges),
                         sorted(
                             lst_dag_general(
                                 g, 1, u,
                                 self.local_cost_func,
                             ).edges()
                         )
                     )

    def test_lst_dag_local_example_2(self):
        g, U, expected_edges_set = get_example_2()
        for u, edges in zip(U, expected_edges_set):
            assert_equal(sorted(edges),
                         sorted(
                             lst_dag_general(
                                 g, 1, u,
                                 self.local_cost_func,
                                 edge_weight_decimal_point=2,
                                 debug=True
                             ).edges()
                         )
                     )

    def test_lst_dag_local_example_3(self):
        g, U, _ = get_example_3()
        expected_edges_set = [
            [],
            [(1, 7)],
            [(1, 'd_1'), ('d_1', 3), (3, 9)],
            [(1, 'd_1'), ('d_1', 3), (3, 9), ('d_1', 2)],
            list(set(g.edges()) - set([(1, 7)]))
        ]
        for u, edges in zip(U, expected_edges_set):
            assert_equal(sorted(edges),
                         sorted(
                             lst_dag_general(
                                 g, 1, u,
                                 self.local_cost_func,
                             ).edges()
                         )
                     )
