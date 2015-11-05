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

    def test_get__meta_graph(self):
        assert_equal(sorted([(1, 2), (1, 3), (2, 4), (1, 4)]),
                     sorted(self.g.edges()))
        assert_equal(self.g.node[1]['body'], 'b1')
        assert_equal(self.g.node[1]['subject'], 's1')
        assert_equal(self.g.node[2]['body'], '...')
        assert_equal(self.g.node[2]['subject'], '...')
        
    def test_add_topics(self):
        lda_model = gensim.models.ldamodel.LdaModel.load('model-4-50.lda')
        dictionary = gensim.corpora.dictionary.Dictionary.load('dictionary.gsm')
        g = EnronUtil.add_topics_to_graph(self.g, lda_model, dictionary)
        for n in g.nodes():
            assert_equal(len(g.node[n]['topics']), 4)
            assert_true(isinstance(g.node[n]['topics'], numpy.ndarray))
