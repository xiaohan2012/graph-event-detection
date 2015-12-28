import unittest

import os
import scipy
import numpy
import gensim
import ujson as json

from datetime import datetime, timedelta
from nose.tools import assert_equal, assert_true, assert_almost_equal

from .interactions import InteractionsUtil

CURDIR = os.path.dirname(os.path.abspath(__file__))


class EnronMetaGraphTest(unittest.TestCase):
    def setUp(self):
        self.lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR, 'test/data/test.lda')
        )
        self.dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
        )
        self.interactions = json.load(
            open(os.path.join(CURDIR,
                              'test/data/enron_test.json')))
        
        self.g = InteractionsUtil.get_meta_graph(
            self.interactions,
            decompose_interactions=True)

    def test_clean_interactions(self):
        assert_equal(self.interactions[3]['recipient_ids'], ["B", "B"])
        cleaned_interactions = InteractionsUtil.clean_interactions(
            self.interactions
        )
        assert_equal(cleaned_interactions[3]['recipient_ids'], ["B"])

    def test_get_meta_graph_without_decomposition(self):
        g = InteractionsUtil.get_meta_graph(
            self.interactions,
            decompose_interactions=False
        )
        assert_equal(sorted([(1, 2), (1, 4), (1, 3),
                             (2, 4), (1, 5), (3, 5)]),
                     sorted(g.edges()))
        assert_equal(5, len(g.nodes()))
                
    def test_get_meta_graph(self):
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(self.g.edges()))
        assert_equal(7, len(self.g.nodes()))
        
        for n in self.g.nodes():
            assert_equal(1,
                         self.g.node[n][InteractionsUtil.VERTEX_REWARD_KEY])
        
        assert_equal(self.g.node['1.B']['body'], 'b1')
        assert_equal(self.g.node['1.B']['message_id'], 1)
        assert_equal(self.g.node['1.B']['subject'], 's1')
        assert_equal(self.g.node['1.B']['timestamp'], 989587576)
        assert_equal(sorted(self.g.node['1.B']['peers']),
                     sorted(['1.B', '1.C', '1.D']))
        assert_equal(self.g.node['1.B']['datetime'],
                     datetime.fromtimestamp(989587576))
        assert_equal(self.g.node['2']['body'], '...')
        assert_equal(self.g.node['2']['message_id'], 2)
        assert_equal(self.g.node['2']['subject'], '...')
        assert_equal(self.g.node['2']['timestamp'], 989587577)
        assert_equal(self.g.node['2']['peers'], [])
        assert_equal(self.g.node['2']['datetime'],
                     datetime.fromtimestamp(989587577))
        
    def _get_topical_graph(self):
        return InteractionsUtil.add_topics_to_graph(self.g,
                                                    self.lda_model,
                                                    self.dictionary)

    def test_add_topics(self):
        g = self._get_topical_graph()
        for n in g.nodes():
            assert_equal(g.node[n]['topics'].shape, (4, ))
            assert_true(isinstance(g.node[n]['topics'], numpy.ndarray))

            # certain fields are deleted and certain fields are added
            assert_true('doc_bow' in g.node[n])

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
            sub_g = InteractionsUtil.filter_dag_given_root(
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
                    InteractionsUtil.get_rooted_subgraph_within_timespan(
                        self.g, '1.D', time_delta.total_seconds()
                    ).edges()
                )
            )
        
    def test_assign_edge_weight(self):
        g = self._get_topical_graph()
        g = InteractionsUtil.assign_edge_weights(g, scipy.stats.entropy)
        
        for s, t in g.edges():
            numpy.testing.assert_array_almost_equal(
                scipy.stats.entropy(g.node[s]['topics'], g.node[t]['topics']),
                g[s][t][InteractionsUtil.EDGE_COST_KEY]
            )
        # 5 is quite different from the rest
        assert_true(g['1.D']['5'][InteractionsUtil.EDGE_COST_KEY] >
                    g['1.D']['3'][InteractionsUtil.EDGE_COST_KEY])

        # the rest are almost equal to each other
        numpy.testing.assert_almost_equal(g['1.D']['4'][InteractionsUtil.EDGE_COST_KEY],
                                          g['2']['4'][InteractionsUtil.EDGE_COST_KEY])

    def test_decompose_interactions(self):
        d_interactions = InteractionsUtil.decompose_interactions(
            InteractionsUtil.clean_interactions(
                self.interactions
            )
        )
        assert_equal(8, len(d_interactions))

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
        assert_equal(decomposed_1[0]['original_message_id'], 1)
        
        decomposed_2 = filter(lambda i: i["recipient_ids"] == ["C"] and
                              i["sender_id"] == "A",
                              d_interactions)
        
        assert_equal(1, len(decomposed_2))
        assert_equal(decomposed_2[0]['message_id'], '1.C')
        assert_equal(decomposed_2[0]['original_message_id'], 1)
        decomposed_3 = filter(lambda i: i["recipient_ids"] == ["D"] and
                              i["sender_id"] == "A",
                              d_interactions)
        
        assert_equal(1, len(decomposed_3))
        assert_equal(decomposed_3[0]['message_id'], '1.D')
        assert_equal(decomposed_3[0]['original_message_id'], 1)

    def test_unzip_interactions(self):
        (interaction_names,
         sources,
         targets,
         time_stamps) = InteractionsUtil.unzip_interactions(
             InteractionsUtil.clean_interactions(
                 self.interactions
             )
         )

        assert_equal(range(1, 7),
                     interaction_names)
        assert_equal(['A', 'A', 'D', 'A', 'D', 'XXX'],
                     sources)
        for e, a in zip([["B", "C", "D"], ['F'], ['E'], ['B'], ['F'], ['XXX']],
                        targets):
            assert_equal(sorted(e), sorted(a))
        assert_equal([989587576, 989587577, 989587578, 989587579,
                      989587580, 989587581],
                     time_stamps)

    def test_get_topic_meta_graph(self):
        g = InteractionsUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy,
                                           preprune_secs=None)
        
        assert_true(
            g['1.D']['5'][InteractionsUtil.EDGE_COST_KEY] >= 0.8
        )
        assert_equal(7, len(g.nodes()))
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(g.edges()))

    def test_get_topic_meta_graph_without_decomposition(self):
        g = InteractionsUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy,
                                           decompose_interactions=False,
                                           preprune_secs=None)
        
        assert_true(
            g[1][5][InteractionsUtil.EDGE_COST_KEY] >= 0.8
        )
        assert_equal(5, len(g.nodes()))
        assert_equal(sorted([(1, 2), (1, 4), (1, 3),
                             (2, 4), (1, 5), (3, 5)]),
                     sorted(g.edges()))

    def test_get_topic_meta_graph_with_prepruning(self):
        g = InteractionsUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy,
                                           preprune_secs=1.0)
        
        assert_almost_equal(
            g['1.D']['2'][InteractionsUtil.EDGE_COST_KEY],
            0
        )
        assert_equal(7, len(g.nodes()))
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2')]),
                     sorted(g.edges()))

    def test_compactize_meta_graph(self):
        # assure node topic vectors are deleted
        g = InteractionsUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy)
        original_g = g.copy()
        g, str2id = InteractionsUtil.compactize_meta_graph(g, map_nodes=True)
        
        for n in original_g.nodes():
            n = str2id[n]
            assert_true('topics' not in g.node[n])
            assert_true('subject' not in g.node[n])
            assert_true('body' not in g.node[n])
            assert_true('peer' not in g.node[n])
            assert_true('doc_bow' not in g.node[n])
            assert_true('message_id' in g.node[n])
            assert_true('sender_id' in g.node[n])
            assert_true('recipient_ids' in g.node[n])
        
        for n in g.nodes():
            assert_true(isinstance(n, int))

        # structure + weight is the same
        for n in original_g.nodes():
            assert_equal(original_g.node[n][InteractionsUtil.VERTEX_REWARD_KEY],
                         g.node[str2id[n]][InteractionsUtil.VERTEX_REWARD_KEY])

        for s, t in original_g.edges():
            s1, t1 = str2id[s], str2id[t]
            assert_equal(original_g[s][t][InteractionsUtil.EDGE_COST_KEY],
                         g[s1][t1][InteractionsUtil.EDGE_COST_KEY])

    def test_compactize_meta_graph_without_node_name_mapping(self):
                # assure node topic vectors are deleted
        g = InteractionsUtil.get_topic_meta_graph(self.interactions,
                                           self.lda_model,
                                           self.dictionary,
                                           dist_func=scipy.stats.entropy)
        original_g = g.copy()
        g = InteractionsUtil.compactize_meta_graph(g, map_nodes=False)

        for n in original_g.nodes():
            assert_true('topics' not in g.node[n])
            assert_true('subject' not in g.node[n])
            assert_true('body' not in g.node[n])
            assert_true('peer' not in g.node[n])
            assert_true('doc_bow' not in g.node[n])
            assert_true('message_id' in g.node[n])
            assert_true('sender_id' in g.node[n])
            assert_true('recipient_ids' in g.node[n])

    def test_preprune_edges_by_timespan(self):
        g = InteractionsUtil.preprune_edges_by_timespan(self.g, 1.0)
        expected_edges = sorted([
            ('1.B', '2'), ('1.C', '2'), ('1.D', '2')
        ])
        assert_equal(expected_edges, sorted(g.edges()))
