import unittest

import numpy
import string
import ujson as json
from nose.tools import assert_equal, assert_true
import gensim
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


class EnronMetaGraphTest(unittest.TestCase):
    def setUp(self):
        interactions = json.load(open('enron_test.json'))
        self.g = EnronUtil.get_meta_graph(interactions)

    def test_get_meta_graph(self):
        assert_equal(sorted([(1, 2), (1, 3), (2, 4), (1, 4)]),
                     sorted(self.g.edges()))
        assert_equal(self.g.node[1]['body'], 'b1')
        assert_equal(self.g.node[1]['subject'], 's1')
        assert_equal(self.g.node[1]['datetime'], 989587576)
        assert_equal(self.g.node[2]['body'], '...')
        assert_equal(self.g.node[2]['subject'], '...')
        assert_equal(self.g.node[2]['datetime'], 989587577)
        
    def test_add_topics(self):
        lda_model = gensim.models.ldamodel.LdaModel.load('model-4-50.lda')
        dictionary = gensim.corpora.dictionary.Dictionary.load('dictionary.gsm')
        g = EnronUtil.add_topics_to_graph(self.g, lda_model, dictionary)
        for n in g.nodes():
            assert_equal(len(g.node[n]['topics']), 4)
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
                self.g.node[n]['datetime'] - self.g.node[r]['datetime'] <= max_time_diff
            )
        assert_equal(sorted(sub_g.edges()), sorted(expected_edges))
        
