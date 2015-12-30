import unittest
import math
from nose.tools import assert_equal
from networkx.classes.digraph import DiGraph

from .lst import lst_dag, lst_dag_general, round_edge_weights_by_multiplying
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
        [],
        [(1, 7)],
        [(1, 'd_1'), ('d_1', 3), (3, 9)],
        [(1, 'd_1'), ('d_1', 3), (3, 9), ('d_1', 2)],
        # (1, 7) removed to make it a tree
        list(set(g.edges()) - set([(1, 7)]))
    ]
    
    return (g, U, expected_edges_set)


def get_example_4():
    g = DiGraph()
    g.add_edges_from([(0, 1), (1, 2), (2, 3), (2, 14),  # tree 1
                      (2, 15), (3, 16), (3, 17),
                      (0, 4), (4, 5), (4, 6),  # tree 2
                      (5, 11), (6, 11), (6, 12), (6, 13),
                      (0, 7), (7, 8), (7, 9),  # tree 3
                      (8, 10), (8, 11), (9, 12), (9, 13)])
    for s, t in g.edges():
        g[s][t]['c'] = 1
    for n in g.nodes():
        g.node[n]['r'] = 1
    g.node[10]['r'] = 2

    U = [7]
    expected_edge_set = [
        [(0, 7), (7, 8), (7, 9),  # tree 3
         (8, 10), (8, 11), (9, 12), (9, 13)]
    ]
    return (g, U, expected_edge_set)


def get_example_4_float():
    g, U, expected_edge_set = get_example_4()
    g = g.copy()
    scaling_factor = float(1e6)
    U = [u / scaling_factor for u in U]
    for s, t in g.edges():
        g[s][t]['c'] = g[s][t]['c'] / scaling_factor

    return (g, U, expected_edge_set)


def get_example_5():
    g = DiGraph()
    g.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4),
                      (2, 4), (2, 5), (2, 6)])
    for s, t in g.edges():
        g[s][t]['c'] = 1
    g[1][4]['c'] = 0
    g[2][4]['c'] = 0
    g[2][6]['c'] = 3
    for n in g.nodes():
        g.node[n]['r'] = 1
    g.node[3]['r'] = 10
    g.node[4]['r'] = 100
    g.node[5]['r'] = 11

    U = [10]
    # sub-optimal answer actually
    expected_edge_set = [[(0, 2), (2, 4), (2, 5), (2, 6)]]
    return (g, U, expected_edge_set)


def get_example_6():
    # IN-OPTIMAL CASE
    g = DiGraph()
    g.add_edges_from([(0, 1), (0, 2), (1, 3),
                      (1, 4), (2, 4), (2, 5)])
    for s, t in g.edges():
        g[s][t]['c'] = 0
    g[1][3]['c'] = 4
    g[1][4]['c'] = 4
    g[2][4]['c'] = 2
    g[2][5]['c'] = 1
    for n in g.nodes():
        g.node[n]['r'] = 0
    g.node[3]['r'] = 1
    g.node[4]['r'] = 100
    g.node[5]['r'] = 1

    U = [7]
    # sub-optimal answer actually
    expected_edge_set = [[(0, 2), (2, 4), (2, 5)]]
    return (g, U, expected_edge_set)


class LstDagTestCase(unittest.TestCase):

    def run_case(self, example_data, **lst_kws):
        original_g, U, expected_edge_list = example_data
        r = 1
        for u, expected in zip(U, expected_edge_list):
            print(u)
            g = original_g.copy()
            actual = lst_dag(g, r, u, **lst_kws)
            assert_equal(sorted(expected),
                         sorted(actual.edges()))

    def test_lst_dag_example_1(self):
        self.run_case(get_example_1())

    def test_lst_dag_example_2(self):
        """
        the case where edge weight are float
        """
        self.run_case(get_example_2(), edge_weight_decimal_point=2)

    def test_lst_dag_example_3(self):
        self.run_case(get_example_3())

    def test_lst_dag_exampl_2_using_floor(self):
        original_g, U, _ = get_example_2()
        r = 1
        expected_edge_list = [
            [],
            [(1, 3)],
            [(1, 2), (2, 4)],
            [(1, 2), (1, 3), (2, 4)],
            [(1, 2), (1, 3), (2, 4)],
            [(1, 2), (1, 3), (2, 4)]
        ]
        for u, expected in zip(U, expected_edge_list):
            g = original_g.copy()
            actual = lst_dag(g, r, u,
                             fixed_point_func=math.floor,
                             edge_weight_decimal_point=2)
            assert_equal(expected, actual.edges())
        

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


def test_round_edge_weights_by_multiplying():
    original_g, U, _ = get_example_4_float()
    U = U[0]
    funcs = [round, math.ceil, math.floor]
    for f in funcs:
        g = original_g.copy()
        new_g, new_U = round_edge_weights_by_multiplying(
            g, U, 6, fixed_point_func=f
        )
        assert_equal(7, new_U)
        for s, t in new_g.edges():
            assert_equal(1, new_g[s][t]['c'])        
