import unittest
import random
import numpy as np

from nose.tools import assert_equal, assert_true, \
    assert_false, assert_almost_equal

import networkx as nx
from sampler import quota_upperbound, UBSampler, RandomSampler, \
    node_scores_from_tree, AdaptiveSampler
    

def test_node_scores_from_tree():
    tree = nx.DiGraph()
    tree.add_edges_from([
        (0, 1), (1, 2), (1, 3), (2, 4), (2, 5),
        (0, 6), (6, 7)
    ])
    for s, t in tree.edges_iter():
        tree[s][t]['c'] = 1
    for n in tree.nodes_iter():
        tree.node[n]['r'] = 1
    scores = node_scores_from_tree(tree, 0)
    assert_equal(
        {0: np.log(9) * 8 / 7,
         1: np.log(6) * 5 / 4,
         2: np.log(4) * 3 / 2,
         6: np.log(3) * 2 / 1},
        scores
    )


class UpperboundTest(unittest.TestCase):
    def setUp(self):
        random.seed(123456)
        g = nx.DiGraph()
        g.add_edges_from([
            (0, 1, {'c': 1}),
            (1, 2, {'c': 1}),
            (0, 2, {'c': 2}),
            (2, 3, {'c': 1}),
        ])
        self.g = g
        for t, n in enumerate(g.nodes_iter()):
            g.node[n]['p'] = 1
            g.node[n]['timestamp'] = t

    def test_quota_upperbound_1(self):
        assert_equal(
            3,
            quota_upperbound(self.g, 0, B=2)
        )

    def test_quota_upperbound_2(self):
        assert_equal(
            4,
            quota_upperbound(self.g, 0, B=100)
        )

    def test_quota_upperbound_3(self):
        assert_equal(
            1,
            quota_upperbound(self.g, 0, B=0)
        )

    def test_ub_sampler(self):
        s = UBSampler(self.g, B=3, timespan_secs=3)
        assert_equal(range(4),
                     s.nodes_sorted_by_upperbound)

        for i in xrange(4):
            node, dag = s.take()
            assert_equal(i, node)
            assert_true(isinstance(dag, nx.DiGraph))

        assert_equal(0,
                     len(s.nodes_sorted_by_upperbound))

    def test_random_sampler(self):
        s = RandomSampler(self.g, timespan_secs=3)
        assert_false([s.take()[0] for i in xrange(4)] == range(4))
        assert_equal(0, len(s.nodes))


class AdaptiveSamplerTest(unittest.TestCase):
    def setUp(self):
        random.seed(123456)

        tree = nx.DiGraph()
        tree.add_edges_from([
            (0, 1), (1, 2), (1, 3), (2, 4), (2, 5),
            (0, 6), (6, 7), (0, 8)
        ])
        self.assign_g_attrs(tree)

        self.tree = tree
        for t, nodes in enumerate([(0, ), (1, 6, 8), (2, 3, 7), (4, 5)]):
            for n in nodes:
                tree.node[n]['timestamp'] = t

        self.s = AdaptiveSampler(self.tree, B=3,
                                 timespan_secs=1,
                                 node_score_func=lambda p, c: p**2 / c)

    def assign_g_attrs(self, tree):
        for s, t in tree.edges_iter():
            tree[s][t]['c'] = 1
        for n in tree.nodes_iter():
            tree.node[n]['r'] = 1

    def test_sampler_init(self):
        assert_equal(
            {0: 4, 1: 3, 2: 3, 6: 2, 8: 1,
             7: 1, 3: 1, 4: 1, 5: 1},
            self.s.root2upperbound
        )

    def test_update(self):
        result_tree = nx.DiGraph()
        result_tree.add_edges_from(
            [(0, 1), (0, 6), (1, 3)]
        )
        self.assign_g_attrs(result_tree)

        self.s.update(0, result_tree)
        assert_equal(
            set([2, 4, 5, 6, 7, 8]),
            self.s.roots_to_explore
        )
        assert_equal(
            set([0, 1, 3]),
            self.s.covered_nodes
        )
        assert_equal(
            {1: 2 ** 2},
            self.s.node2score
        )

        # case: score of node 1 increases
        result_tree.add_edge(1, 2)
        self.assign_g_attrs(result_tree)

        self.s.update(0, result_tree)
        assert_equal(
            {1: 3 ** 2 / 2},
            self.s.node2score
        )

    def test_update_edge_case(self):
        self.s.update(0, self.tree)
        assert_equal(
            set(range(9)),
            self.s.covered_nodes
        )
        assert_equal(0,
                     self.s.explore_proba)

    def test_explore_proba(self):
        assert_equal(1, self.s.explore_proba)

        result_tree = nx.DiGraph()
        result_tree.add_edges_from(
            [(0, 1), (0, 6), (1, 3)]
        )
        self.assign_g_attrs(result_tree)
        self.s.update(0, result_tree)

        assert_almost_equal(6 / 9., self.s.explore_proba)

    def test_take_via_explore(self):
        r, tree = self.s.take()
        assert_equal('explore',
                     self.s.random_action())
        assert_equal(0, r)
        assert_equal(
            sorted([(0, 1), (0, 6), (0, 8)]),
            sorted(tree.edges())
        )

    def test_take_via_exploit(self):
        # round 2
        self.s.update(0, self.tree)
        assert_equal('exploit',
                     self.s.random_action())
        r, tree = self.s.take()
        assert_equal(1, r)
