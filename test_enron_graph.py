import unittest

import os
import scipy
import numpy
import gensim
import ujson as json

from datetime import datetime
from nose.tools import assert_equal, assert_true

from .enron_graph import EnronUtil

CURDIR = os.path.dirname(os.path.abspath(__file__))


class EnronMetaGraphTest(unittest.TestCase):
    def setUp(self):
        interactions = json.load(open(os.path.join(CURDIR, 'enron_test.json')))
        self.g = EnronUtil.get_meta_graph(interactions)

    def test_get_meta_graph(self):
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(self.g.edges()))
        assert_equal(7, len(self.g.nodes()))
        
        assert_equal(self.g.node['1.B']['body'], 'b1')
        assert_equal(self.g.node['1.B']['subject'], 's1')
        assert_equal(self.g.node['1.B']['timestamp'], 989587576)
        assert_equal(self.g.node['1.B']['datetime'],
                     datetime.fromtimestamp(989587576))
        assert_equal(self.g.node['2']['body'], '...')
        assert_equal(self.g.node['2']['subject'], '...')
        assert_equal(self.g.node['2']['timestamp'], 989587577)
        assert_equal(self.g.node['2']['datetime'],
                     datetime.fromtimestamp(989587577))
        
    def _get_topical_graph(self):
        lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR, 'model-4-50.lda')
        )
        dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR, 'dictionary.gsm')
        )
        return EnronUtil.add_topics_to_graph(self.g, lda_model, dictionary)

    # DEPRECATED
    # def _get_vertex_weighted_graph(self):
    #     g = self._get_topical_graph()
    #     ref_vect = numpy.asarray([0, 0, 1, 0], dtype=numpy.float)
    #     return EnronUtil.assign_vertex_weight(
    #         g, ref_vect,
    #         dist_func=scipy.stats.entropy
    #     )
        
    def test_add_topics(self):
        g = self._get_topical_graph()
        for n in g.nodes():
            assert_equal(g.node[n]['topics'].shape, (4, ))
            assert_true(isinstance(g.node[n]['topics'], numpy.ndarray))

    def test_filter_nodes_given_root(self):
        r = '1.D'
        max_time_diffs = range(5)  # 0 ... 4 secs
        expected_edges_list = [
            [],
            [('1.D', '2')],
            [('1.D', '2'), ('1.D', '3')],
            [('1.D', '2'), ('1.D', '3'), ('1.D', '4'), ('2', '4')],
            [('1.D', '2'), ('1.D', '3'), ('1.D', '4'), ('2', '4'),
             ('1.D', u'5'), ('3', u'5')]
        ]
        for max_time_diff, expected_edges in \
            zip(max_time_diffs, expected_edges_list):
            sub_g = EnronUtil.filter_dag_given_root(
                self.g, r,
                lambda n:
                self.g.node[n]['timestamp'] - self.g.node[r]['timestamp'] <= max_time_diff
            )
        assert_equal(sorted(sub_g.edges()), sorted(expected_edges))

    # DEPRECATED
    # def test_assign_vertex_weight(self):
    #     ref_vect = numpy.asarray([0, 0, 1, 0],
    #                              dtype=numpy.float)  # the 'enronxgate'
    #     g = self._get_topical_graph()
    #     for n in g.nodes():
    #         assert_true('w' not in g.node[n])
    #     entropy = scipy.stats.entropy
    #     g = EnronUtil.assign_vertex_weight(
    #         g, ref_vect,
    #         dist_func=entropy
    #     )
    #     for n in g.nodes():
    #         numpy.testing.assert_array_almost_equal(
    #             entropy(ref_vect, g.node[n]['topics']),
    #             g.node[n]['w']
    #         )
    #     assert_equal(numpy.argmax([g.node[n]['w'] for n in g.nodes()]),
    #                  4)

    # def test_round_vertex_weight(self):
    #     g = self._get_vertex_weighted_graph()
        
    #     g = EnronUtil.round_vertex_weight(g)
    #     expected_values = [1, 1, 1, 1, 3]
    #     for n, expected in zip(g.nodes(), expected_values):
    #         assert_equal(g.node[n]['r_w'], expected)

    def test_assign_edge_weight(self):
        g = self._get_topical_graph()
        g = EnronUtil.assign_edge_weights(g, scipy.stats.entropy)
        
        for s, t in g.edges():
            print(s, t, g.node[s]['topics'], g.node[t]['topics'],
                  g[s][t]['w'])
            numpy.testing.assert_array_almost_equal(
                scipy.stats.entropy(g.node[s]['topics'], g.node[t]['topics']),
                g[s][t]['w']
            )
        # 5 is quite different from the rest
        assert_true(g['1.D']['5']['w'] > g['1.D']['3']['w'])
        # the rest are almost equal to each other
        numpy.testing.assert_almost_equal(g['1.D']['4']['w'], g['2']['4']['w'])

    def test_decompose_interactions(self):
        interactions = json.load(open('enron_test.json'))
        d_interactions = EnronUtil.decompose_interactions(interactions)
        assert_equal(7, len(d_interactions))

        # ['B', 'C', 'D'] should be decomposed
        assert_equal(0,
                     len(filter(lambda i:
                                i["recipient_ids"] == ["B", "C", "D"],
                                d_interactions)))
        decomposed_1 = filter(lambda i: i["recipient_ids"] == ["B"] and
                              i["sender_id"] == "A",
                              d_interactions)
        assert_equal(2, len(decomposed_1))  # originally, we have an A->B
        assert_equal(decomposed_1[1]['message_id'], '4')  # check if name is convered to string
        assert_equal(decomposed_1[0]['message_id'], '1.B')
        
        decomposed_2 = filter(lambda i: i["recipient_ids"] == ["C"] and
                              i["sender_id"] == "A",
                              d_interactions)
        
        assert_equal(1, len(decomposed_2))
        assert_equal(decomposed_2[0]['message_id'], '1.C')
        
        decomposed_3 = filter(lambda i: i["recipient_ids"] == ["D"] and
                              i["sender_id"] == "A",
                              d_interactions)
        
        assert_equal(1, len(decomposed_3))
        assert_equal(decomposed_3[0]['message_id'], '1.D')

    def test_unzip_interactions(self):
        interactions = json.load(open('enron_test.json'))
        interaction_names, sources, targets, time_stamps = EnronUtil.unzip_interactions(interactions)
        assert_equal(range(1, 6),
                     interaction_names)
        assert_equal(['A', 'A', 'D', 'A', 'D'],
                     sources)
        assert_equal([["B", "C", "D"], ['F'], ['E'], ['B'], ['F']],
                     targets)
        assert_equal([989587576, 989587577, 989587578, 989587579, 989587580],
                     time_stamps)
        
        
        
