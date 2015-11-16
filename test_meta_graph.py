import unittest

import scipy
import numpy
import string
import gensim
import ujson as json

from datetime import datetime
from nose.tools import assert_equal, assert_true

from .meta_graph import convert_to_meta_graph, EnronUtil


def test_meta_graph():
    A, B, C, D, E, F, G = string.ascii_uppercase[:7]
    node_names = range(1, 6)
    sources = [A, A, D, A, G]
    targets = [(B, C, D), (F, ), (E, ), (B, ), (F, )]
    time_stamps = range(1, 6)
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)
    expected_edges = sorted([(1, 2), (1, 3), (2, 4), (1, 4)])
    assert_equal(expected_edges, sorted(graph.edges()))


def test_meta_graph_1():
    a, b, c, d = 'a', 'b', 'c', 'd'
    node_names = range(1, 6)
    sources = [a, a, b, d, b]
    targets = [c, b, a, c, d]
    time_stamps = [1, 1, 2, 2, 3]
    
    g = convert_to_meta_graph(node_names, sources, targets, time_stamps)
    
    expected_edges = sorted([(2, 3), (3, 5), (2, 5)])
    assert_equal(expected_edges, sorted(g.edges()))


class EnronMetaGraphTest(unittest.TestCase):
    def setUp(self):
        interactions = json.load(open('enron_test.json'))
        self.g = EnronUtil.get_meta_graph(interactions)

    def test_get_meta_graph(self):
        assert_equal(sorted([(1, 2), (1, 3), (2, 4), (1, 4)]),
                     sorted(self.g.edges()))
        assert_equal(self.g.node[1]['body'], 'b1')
        assert_equal(self.g.node[1]['subject'], 's1')
        assert_equal(self.g.node[1]['timestamp'], 989587576)
        assert_equal(self.g.node[1]['datetime'],
                     datetime.fromtimestamp(989587576))
        assert_equal(self.g.node[2]['body'], '...')
        assert_equal(self.g.node[2]['subject'], '...')
        assert_equal(self.g.node[2]['timestamp'], 989587577)
        assert_equal(self.g.node[2]['datetime'],
                     datetime.fromtimestamp(989587577))
        
    def _get_topical_graph(self):
        lda_model = gensim.models.ldamodel.LdaModel.load('model-4-50.lda')
        dictionary = gensim.corpora.dictionary.Dictionary.load('dictionary.gsm')
        return EnronUtil.add_topics_to_graph(self.g, lda_model, dictionary)

    def _get_weighted_graph(self):
        g = self._get_topical_graph()
        ref_vect = numpy.asarray([0, 0, 1, 0], dtype=numpy.float)
        return EnronUtil.assign_vertex_weight(
            g, ref_vect,
            dist_func=scipy.stats.entropy
        )
        
    def test_add_topics(self):
        g = self._get_topical_graph()
        for n in g.nodes():
            assert_equal(g.node[n]['topics'].shape, (4, ))
            assert_true(isinstance(g.node[n]['topics'], numpy.ndarray))

    def test_filter_nodes_given_root(self):
        r = 1
        max_time_diffs = range(5)  # 0 ... 4 secs
        expected_edges_list = [
            [],
            [(1, 2)],
            [(1, 2), (1, 3)],
            [(1, 2), (1, 3), (1, 4), (2, 4)],
            [(1, 2), (1, 3), (1, 4), (2, 4)]
        ]
        for max_time_diff, expected_edges in \
            zip(max_time_diffs, expected_edges_list):
            sub_g = EnronUtil.filter_dag_given_root(
                self.g, r,
                lambda n:
                self.g.node[n]['timestamp'] - self.g.node[r]['timestamp'] <= max_time_diff
            )
        assert_equal(sorted(sub_g.edges()), sorted(expected_edges))

    def test_assign_vertex_weight(self):
        ref_vect = numpy.asarray([0, 0, 1, 0],
                                 dtype=numpy.float)  # the 'enronxgate'
        g = self._get_topical_graph()
        for n in g.nodes():
            assert_true('w' not in g.node[n])
        entropy = scipy.stats.entropy
        g = EnronUtil.assign_vertex_weight(
            g, ref_vect,
            dist_func=entropy
        )
        for n in g.nodes():
            numpy.testing.assert_array_almost_equal(
                entropy(ref_vect, g.node[n]['topics']),
                g.node[n]['w']
            )
        assert_equal(numpy.argmax([g.node[n]['w'] for n in g.nodes()]),
                     4)

    def test_round_vertex_weight(self):
        g = self._get_weighted_graph()
        
        g = EnronUtil.round_vertex_weight(g)
        expected_values = [1, 1, 1, 1, 3]
        for n, expected in zip(g.nodes(), expected_values):
            assert_equal(g.node[n]['r_w'], expected)
        
