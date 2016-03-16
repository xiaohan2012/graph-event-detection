import networkx as nx
import string
import unittest
from nose.tools import assert_equal

from budget_problem import charikar_algo, transitive_closure, \
    binary_search_using_charikar


R = 'root'
A, B, C, D, E, F, G = string.lowercase[:7]
EPS = 0.0001


class CharikarAlgoTest(unittest.TestCase):
    def setUp(self):
        # the 'bunch' example in Charikar's paper
        g = nx.DiGraph()
        g.add_path([R, A, B, C, D, E])
        g.add_edges_from([(A, C), (A, D), (A, E)])
        for n in g.nodes_iter():
            g.node[n]['r'] = 1
        for n in [B, C, D, E]:
            g[A][n]['c'] = 10
        for s, t in zip([B, C, D], [C, D, E]):
            g[s][t]['c'] = EPS
        g[R][A]['c'] = EPS
        self.g1 = g

    def test_transitive_closure(self):
        new_g, sp_table = transitive_closure(self.g1)
        assert_equal(10 + EPS, new_g[R][B]['c'])
        assert_equal(EPS * 2, new_g[B][D]['c'])
        assert_equal(EPS * 3, new_g[B][E]['c'])
        assert_equal(10, new_g[A][D]['c'])
        assert_equal([R, A, C],
                     sp_table[R][C])

    def check_level(self, level, edges, k=5, root=R, X=[A, B, C, D, E]):
        actual = charikar_algo(self.g1, root,
                               X,
                               k, level)
        assert_equal(sorted(edges),
                     sorted(actual.edges())
        )

    def test_return_empty(self):
        actual = charikar_algo(self.g1, R,
                               [A, B, C, D, E],
                               100, 1)
        assert_equal([],
                     actual.edges()
                 )

    def test_level_1(self):
        self.check_level(
            1,
            [(R, A), (A, B), (A, C), (A, D), (A, E)]
        )

    def check_level_1_another(self):
        self.check_level(1,
                         edges=[(C, D), (D, E)],
                         k=1,
                         root=C,
                         X=[B, E]
        )

    def test_level_2(self):
        self.check_level(
            2,
            [(R, A), (A, B), (B, C), (C, D), (D, E)]
        )

    def test_level_2_extra_level(self):
        self.check_level(
            level=2,
            edges=[(A, B)],
            X=[B, E],
            root=A,
            k=1
        )

    def test_level_100(self):
        self.check_level(
            100,
            [(R, A), (A, B), (B, C), (C, D), (D, E)]
        )

    def check_binary_search(self, B, edges, level=2):
        t = binary_search_using_charikar(
            self.g1, R,
            B=B,
            level=3
        )

        assert_equal(
            sorted(edges),
            sorted(t.edges())
        )

    def check_bs_zero_budget(self):
        self.check_binary_search(
            B=0,
            edges=[]
        )

    def check_bs_infinite_budget(self):
        self.check_binary_search(
            B=100,
            edges=[(R, A), (A, B), (B, C), (C, D), (D, E)]
        )

    def check_bs_just_enough_budget(self):
        self.check_binary_search(
            B=10 + 4 * EPS,
            edges=[(R, A), (A, B), (B, C), (C, D), (D, E)]
        )
