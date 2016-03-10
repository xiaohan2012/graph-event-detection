import unittest
import networkx as nx
from nose.tools import assert_equal, assert_almost_equal

from tree_util import to_bracket_notation, salzburg_ted, \
    tree_similarity_ratio, tree_density


class TestCase(unittest.TestCase):
    def setUp(self):
        t1 = nx.DiGraph()
        t1.add_edges_from([
            ('A', 'B'),
            ('B', 'X'),
            ('B', 'Y'),
            ('B', 'F'),
            ('A', 'C'),
        ])
        for s, t in t1.edges_iter():
            t1[s][t]['c'] = 1

        t2 = nx.DiGraph()
        t2.add_edges_from([
            ('A', 'B'),
            ('B', 'X'),
            ('B', 'Y'),
            ('B', 'F'),
            ('A', 'D'),
        ])
        self.t1, self.t2 = t1, t2

    def test_to_bracket_notation(self):
        assert_equal(
            '{A{B{F}{X}{Y}}{C}}',
            to_bracket_notation(self.t1)
        )

    def test_salzburg_ted(self):
        assert_equal(
            1.0,
            salzburg_ted(self.t1, self.t2)
        )

    def test_tree_similarity_ratio(self):
        assert_equal(10. / 12,
                     tree_similarity_ratio(1.0, self.t1, self.t2))

    def test_tree_density(self):
        X = set(['A', 'B', 'C', 'D'])

        assert_almost_equal(
            5 / 3.0,
            tree_density(self.t1, X)
        )

    def test_tree_density_inf(self):
        assert_equal(
            float('inf'),
            tree_density(self.t1, set())
        )
