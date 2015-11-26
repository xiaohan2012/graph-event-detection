import unittest

import os
import scipy
import numpy
import gensim
import ujson as json

from datetime import datetime, timedelta
from nose.tools import assert_equal, assert_true, assert_almost_equal

from .enron_graph import EnronUtil

CURDIR = os.path.dirname(os.path.abspath(__file__))


class EnronMetaGraphTest(unittest.TestCase):
    def setUp(self):
        self.lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR, 'test/data/test.lda')
        )
        self.dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
        )
        self.interactions = json.load(open(os.path.join(CURDIR,
                                                        'test/data/enron_test.json')))
        
        self.g = EnronUtil.get_meta_graph(self.interactions)

    def test_clean_interactions(self):
        assert_equal(self.interactions[3]['recipient_ids'], ["B", "B"])
        cleaned_interactions = EnronUtil.clean_interactions(
            self.interactions
        )
        assert_equal(cleaned_interactions[3]['recipient_ids'], ["B"])

    def test_get_meta_graph(self):
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(self.g.edges()))
        assert_equal(7, len(self.g.nodes()))
        
        for n in self.g.nodes():
            assert_equal(1,
                         self.g.node[n][EnronUtil.VERTEX_REWARD_KEY])
        
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
        return EnronUtil.add_topics_to_graph(self.g, self.lda_model, self.dictionary)

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
                self.g.node[n]['timestamp'] - self.g.node[r]['timestamp'] <= max_time_diff,
            )
            assert_equal(sorted(sub_g.edges()), sorted(expected_edges))

            # make sure attributes are copied
            for s, t in sub_g.edges():
                assert_equal(sub_g[s][t], self.g[s][t])

            for n in sub_g.nodes():
                assert_equal(sub_g.node[n], self.g.node[n])

    def test_get_rooted_subgraph_within_timespan(self):
        time_deltas = [timedelta(seconds=i)
                       for i in range(5)]  # 0 ... 4 secs
        expected_edges_list = [
            [],
            [('1.D', '2')],
            [('1.D', '2'), ('1.D', '3')],
            [('1.D', '2'), ('1.D', '3'), ('1.D', '4'), ('2', '4')],
            [('1.D', '2'), ('1.D', '3'), ('1.D', '4'), ('2', '4'),
             ('1.D', u'5'), ('3', u'5')]
        ]
        for time_delta, expected_edges in \
            zip(time_deltas, expected_edges_list):
            assert_equal(
                sorted(expected_edges),
                sorted(
                    EnronUtil.get_rooted_subgraph_within_timespan(
                        self.g, '1.D', time_delta.total_seconds()
                    ).edges()
                )
            )
        
    def test_assign_edge_weight(self):
        g = self._get_topical_graph()
        g = EnronUtil.assign_edge_weights(g, scipy.stats.entropy)
        
        for s, t in g.edges():
            numpy.testing.assert_array_almost_equal(
                scipy.stats.entropy(g.node[s]['topics'], g.node[t]['topics']),
                g[s][t][EnronUtil.EDGE_COST_KEY]
            )
        # 5 is quite different from the rest
        assert_true(g['1.D']['5'][EnronUtil.EDGE_COST_KEY] >
                    g['1.D']['3'][EnronUtil.EDGE_COST_KEY])
        # the rest are almost equal to each other
        numpy.testing.assert_almost_equal(g['1.D']['4'][EnronUtil.EDGE_COST_KEY],
                                          g['2']['4'][EnronUtil.EDGE_COST_KEY])

    def test_decompose_interactions(self):
        d_interactions = EnronUtil.decompose_interactions(
            EnronUtil.clean_interactions(
                self.interactions
            )
        )
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
        (interaction_names,
         sources,
         targets,
         time_stamps) = EnronUtil.unzip_interactions(
             EnronUtil.clean_interactions(
                 self.interactions
             )
         )

        assert_equal(range(1, 6),
                     interaction_names)
        assert_equal(['A', 'A', 'D', 'A', 'D'],
                     sources)
        for e, a in zip([["B", "C", "D"], ['F'], ['E'], ['B'], ['F']],
                        targets):
            assert_equal(sorted(e), sorted(a))
        assert_equal([989587576, 989587577, 989587578, 989587579, 989587580],
                     time_stamps)
        
    def test_get_topic_meta_graph(self):
        g = EnronUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy)
        
        assert_almost_equal(
            g['1.D']['5'][EnronUtil.EDGE_COST_KEY],
            0.1511326,
            places=4
        )
        assert_equal(7, len(g.nodes()))
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(g.edges()))
    
