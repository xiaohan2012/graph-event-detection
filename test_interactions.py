import unittest

import os
import scipy
import numpy
import gensim
import ujson as json

from datetime import datetime, timedelta
from nose.tools import assert_equal, assert_true, assert_almost_equal
from scipy.spatial.distance import euclidean, cosine, jaccard
from scipy.sparse import issparse

from sklearn.feature_extraction.text import TfidfVectorizer

from .dag_util import binarize_dag
from .interactions import InteractionsUtil as IU,\
    clean_decom_unzip, clean_unzip

CURDIR = os.path.dirname(os.path.abspath(__file__))


class InteractionsUtilTest(unittest.TestCase):
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
        self.g = IU.get_meta_graph(
            self.interactions,
            decompose_interactions=True
        )

        self.g_undecom = IU.get_meta_graph(
            self.interactions,
            decompose_interactions=False
        )

    def test_clean_interactions(self):
        assert_equal(self.interactions[3]['recipient_ids'], ["B", "B"])
        cleaned_interactions = IU.clean_interactions(
            self.interactions
        )
        assert_equal(cleaned_interactions[3]['recipient_ids'], ["B"])
        assert_true(isinstance(cleaned_interactions[3]['datetime'],
                               datetime))
        assert_true(isinstance(cleaned_interactions[1]['timestamp'],
                               float))

    def test_get_meta_graph_without_decomposition(self):
        g = IU.get_meta_graph(
            self.interactions,
            decompose_interactions=False
        )
        assert_equal(sorted([(1, 2), (1, 4), (1, 3),
                             (2, 4), (1, 5), (3, 5)]),
                     sorted(g.edges()))
        assert_equal(5, len(g.nodes()))
        for n in g.nodes():
            assert_true(isinstance(g.node[n]['datetime'], datetime))
            assert_true(isinstance(g.node[n]['timestamp'], float))

    def test_get_meta_graph_with_pagerank(self):
        new_mg = IU.get_meta_graph(self.interactions,
                                   decompose_interactions=False,
                                   apply_pagerank=True)
        assert_true(new_mg.node[1]['r'] != 1)
        assert_true(new_mg.node[1]['r'] < new_mg.node[5]['r'])
            
    def test_get_meta_graph(self):
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(self.g.edges()))
        assert_equal(7, len(self.g.nodes()))
        
        for n in self.g.nodes():
            assert_equal(1,
                         self.g.node[n][IU.VERTEX_REWARD_KEY])
            assert_true('hashtags' in self.g.node[n])
        
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
        return IU.add_topics_to_graph(self.g,
                                      self.lda_model,
                                      self.dictionary)

    def test_add_topics(self):
        g = self._get_topical_graph()
        for n in g.nodes():
            assert_equal(g.node[n]['topics'].shape, (4, ))
            assert_true(isinstance(g.node[n]['topics'], numpy.ndarray))

            # certain fields are deleted and certain fields are added
            assert_true('doc_bow' in g.node[n])

    def test_build_bow_matrix(self):
        n2i, mat = IU.build_bow_matrix(self.g_undecom, self.dictionary)
        self.assertEqual(0,
                         n2i[next(self.g_undecom.nodes_iter())])
        self.assertEqual(
            (self.g_undecom.number_of_nodes(), len(self.dictionary.keys())),
            mat.shape
        )

    def test_add_hashtag_bow_to_graph(self):
        g = IU.add_hastag_bow_to_graph(self.g_undecom)
        tfidf = TfidfVectorizer(preprocessor=None,
                                tokenizer=lambda s: s.split(),
                                stop_words=None)
        tfidf.fit([' '.join(g.node[n]['hashtags'])
                   for n in g.nodes_iter()])

        for n in g.nodes_iter():
            assert_true(issparse(g.node[n]['hashtag_bow']))
            assert_equal(
                sorted(g.node[n]['hashtags']),
                sorted(
                    tfidf.inverse_transform(
                        g.node[n]['hashtag_bow']
                    )[0].tolist()
                )
            )

    def test_add_bow_to_graph(self):
        IU.add_bow_to_graph(self.g_undecom, self.dictionary)
        g = self.g_undecom
        for n in g.nodes_iter():
            assert_true(issparse(g.node[n]['bow']))

            doc = u'{} {}'.format(g.node[n]['subject'], g.node[n]['body'])
            bow = self.dictionary.doc2bow(IU.tokenize_document(doc))

            for id_, cnt in bow:
                # word feature values are positive
                assert_true(g.node[n]['bow'][0, id_] > 0)
                # tfidf takes effect
                assert_true(g.node[n]['bow'][0, id_] != cnt)

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
            sub_g = IU.filter_dag_given_root(
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
                    IU.get_rooted_subgraph_within_timespan(
                        self.g, '1.D', time_delta.total_seconds()
                    ).edges()
                )
            )

    def _get_topic_graph_with_edge_cost(self):
        g = self._get_topical_graph()
        return IU.assign_edge_weights(g, scipy.stats.entropy)

    def test_get_rooted_subgraph_within_timespan_with_binarization(self):
        g = self._get_topic_graph_with_edge_cost()
        sub_dag = IU.get_rooted_subgraph_within_timespan(
            g, '1.D', 4
        )
        bin_dag = binarize_dag(sub_dag,
                               IU.VERTEX_REWARD_KEY,
                               IU.EDGE_COST_KEY,
                               dummy_node_name_prefix="d_")
        bin_dag

    def test_assign_edge_weight_single_field(self):
        g = self._get_topical_graph()
        g = IU.assign_edge_weights(g, scipy.stats.entropy)
        
        for s, t in g.edges():
            numpy.testing.assert_array_almost_equal(
                scipy.stats.entropy(g.node[s]['topics'], g.node[t]['topics']),
                g[s][t][IU.EDGE_COST_KEY]
            )
        # 5 is quite different from the rest
        assert_true(g['1.D']['5'][IU.EDGE_COST_KEY] >
                    g['1.D']['3'][IU.EDGE_COST_KEY])

        # the rest are almost equal to each other
        numpy.testing.assert_almost_equal(g['1.D']['4'][IU.EDGE_COST_KEY],
                                          g['2']['4'][IU.EDGE_COST_KEY])

    def test_assign_edge_weight_two_fields(self):
        g = self._get_topical_graph()
        IU.add_bow_to_graph(g, self.dictionary)
        g = IU.assign_edge_weights(
            g,
            cosine,
            fields_with_weights={'topics': 0.2, 'bow': 0.8}
        )
        
        self.check_weighted_dist(g, self.weight_cost_func_bow_topics)

    def test_decompose_interactions(self):
        d_interactions = IU.decompose_interactions(
            IU.clean_interactions(
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
        # check if name is convered to string
        assert_equal(decomposed_1[1]['message_id'], '4')
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
         time_stamps) = clean_unzip(self.interactions)

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
        g = IU.get_topic_meta_graph(
            self.interactions,
            scipy.stats.entropy,
            self.lda_model,
            self.dictionary,
            preprune_secs=None)
        
        assert_true(
            g['1.D']['5'][IU.EDGE_COST_KEY] >= 0.8
        )
        assert_equal(7, len(g.nodes()))
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4'), ('1.D', '5'),
                             ('3', '5')]),
                     sorted(g.edges()))

    def weight_cost_func_bow_topics(self, s, t):
        a1 = numpy.array(s['bow'].todense()).ravel()
        a2 = numpy.array(t['bow'].todense()).ravel()
        if not a1.any() or not a2.any():
            d = 1
        else:
            d = cosine(a1, a2)
        return (0.2 * cosine(s['topics'], t['topics']) +
                0.8 * d)

    def weight_cost_func_hashtag_bow_topics(self, s, t):
        a1 = numpy.array(s['hashtag_bow'].todense()).ravel()
        a2 = numpy.array(t['hashtag_bow'].todense()).ravel()
        if not a1.any() or not a2.any():
            d = 1
        else:
            d = jaccard(a1, a2)
        return (0.2 * cosine(s['topics'], t['topics']) +
                0.1 * d)

    def check_weighted_dist(
            self, g, cost_func):
        for s, t in g.edges():
            self.assertFalse(
                numpy.isnan(g[s][t][IU.EDGE_COST_KEY])
            )
            self.assertFalse(
                numpy.isinf(g[s][t][IU.EDGE_COST_KEY])
            )
            
            numpy.testing.assert_array_almost_equal(
                g[s][t][IU.EDGE_COST_KEY],
                cost_func(g.node[s], g.node[t])
            )

    def test_get_topic_meta_graph_multiple_reprs(self):
        g = IU.get_topic_meta_graph(
            self.interactions,
            cosine,
            self.lda_model,
            self.dictionary,
            preprune_secs=None,
            distance_weights={
                'topics': 0.2,
                'bow': 0.8
            }
        )

        self.check_weighted_dist(g, self.weight_cost_func_bow_topics)

    def test_get_topic_meta_graph_using_hashtag_bow(self):
        g = IU.get_topic_meta_graph(
            self.interactions,
            cosine,
            self.lda_model,
            self.dictionary,
            preprune_secs=None,
            distance_weights={
                'topics': 0.2,
                'hashtag_bow': 0.1
            }
        )

        self.check_weighted_dist(
            g,
            self.weight_cost_func_hashtag_bow_topics
        )

    def test_get_topic_meta_graph_without_decomposition(self):
        g = IU.get_topic_meta_graph(self.interactions,
                                    scipy.stats.entropy,
                                    self.lda_model,
                                    self.dictionary,
                                    decompose_interactions=False,
                                    preprune_secs=None)
        
        assert_true(
            g[1][5][IU.EDGE_COST_KEY] >= 0.8
        )
        assert_equal(5, len(g.nodes()))
        assert_equal(sorted([(1, 2), (1, 4), (1, 3),
                             (2, 4), (1, 5), (3, 5)]),
                     sorted(g.edges()))

    def test_get_topic_meta_graph_with_prepruning(self):
        g = IU.get_topic_meta_graph(self.interactions,
                                    scipy.stats.entropy,
                                    self.lda_model,
                                    self.dictionary,
                                    preprune_secs=1.0)
        
        assert_almost_equal(
            g['1.D']['2'][IU.EDGE_COST_KEY],
            0
        )
        assert_equal(sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2')]),
                     sorted(g.edges()))

    def test_get_topic_meta_graph_with_pagerank(self):
        new_mg = IU.get_topic_meta_graph(
            self.interactions,
            scipy.stats.entropy,
            self.lda_model,
            self.dictionary,
            preprune_secs=None,
            apply_pagerank=True,
            decompose_interactions=False)
        assert_true(new_mg.node[1]['r'] != 1)
        assert_true(new_mg.node[1]['r'] < new_mg.node[5]['r'])

    def test_compactize_meta_graph(self):
        # assure node topic vectors are deleted
        g = IU.get_topic_meta_graph(self.interactions,
                                    scipy.stats.entropy,
                                    self.lda_model,
                                    self.dictionary)
        original_g = g.copy()
        g, str2id = IU.compactize_meta_graph(g, map_nodes=True)
        
        for n in original_g.nodes():
            n = str2id[n]
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
            assert_equal(original_g.node[n][IU.VERTEX_REWARD_KEY],
                         g.node[str2id[n]][IU.VERTEX_REWARD_KEY])

        for s, t in original_g.edges():
            s1, t1 = str2id[s], str2id[t]
            assert_equal(original_g[s][t][IU.EDGE_COST_KEY],
                         g[s1][t1][IU.EDGE_COST_KEY])

    def test_compactize_meta_graph_without_node_name_mapping(self):
                # assure node topic vectors are deleted
        g = IU.get_topic_meta_graph(
            self.interactions,
            scipy.stats.entropy,
            self.lda_model,
            self.dictionary
        )
        original_g = g.copy()
        g = IU.compactize_meta_graph(g, map_nodes=False)

        for n in original_g.nodes():
            assert_true('subject' not in g.node[n])
            assert_true('body' not in g.node[n])
            assert_true('peer' not in g.node[n])
            assert_true('doc_bow' not in g.node[n])
            assert_true('message_id' in g.node[n])
            assert_true('sender_id' in g.node[n])
            assert_true('recipient_ids' in g.node[n])

    def test_preprune_edges_by_timespan(self):
        g = IU.preprune_edges_by_timespan(self.g, 1.0)
        expected_edges = sorted([
            ('1.B', '2'), ('1.C', '2'), ('1.D', '2')
        ])
        assert_equal(expected_edges, sorted(g.edges()))

    def test_preprune_edges_by_timespan_on_binary_dag(self):
        g = IU.preprune_edges_by_timespan(self.g, 1.0)
        expected_edges = sorted([
            ('1.B', '2'), ('1.C', '2'), ('1.D', '2')
        ])
        assert_equal(expected_edges, sorted(g.edges()))

    def test_add_rewards_to_nodes(self):
        new_g = IU.add_rewards_to_nodes(self.g,
                                        reward_func=lambda n: 0.1)
        for n in new_g.nodes_iter():
            assert_equal(0.1, new_g.node[n]['r'])
        
    def test_add_rewards_to_nodes_using_pagerank(self):
        cleaned_interactions = IU.clean_interactions(self.interactions)
        mg = IU.get_meta_graph(cleaned_interactions,
                               decompose_interactions=False)
        new_mg = IU.add_rewards_to_nodes_using_pagerank(
            mg,
            cleaned_interactions
        )
        assert_true(new_mg.node[1]['r'] < new_mg.node[5]['r'])

    def _get_meta_graph(self):
        cleaned_interactions = IU.clean_interactions(self.interactions)
        mg = IU.get_topic_meta_graph(cleaned_interactions,
                                     cosine,
                                     self.lda_model,
                                     self.dictionary,
                                     decompose_interactions=False)
        return IU.assign_edge_weights(mg, cosine)

    def test_add_recency(self):
        g_before = self._get_meta_graph()
        g = IU.add_recency(g_before.copy(),
                           alpha=1.0, tau=0.8,
                           timestamp_converter=lambda s: 2*s)
        assert_almost_equal(
            g_before[1][2]['c'] - 1.0 * (0.8 ** 2),
            g[1][2]['c']
        )

    def test_get_topic_meta_graph_with_recency(self):
        g_before = self._get_meta_graph()
        g = IU.get_topic_meta_graph(
            IU.clean_interactions(self.interactions),
            cosine,
            lda_model=self.lda_model,
            dictionary=self.dictionary,
            decompose_interactions=False,
            consider_recency=True,
            alpha=0.5,
            tau=0.6
        )
        assert_almost_equal(
            g_before[1][2]['c'] - 0.5 * (0.6 ** 1),
            g[1][2]['c']
        )


class InteractionsUtilTestUndirected(unittest.TestCase):
    """undirected case
    """
    def setUp(self):
        self.lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR, 'test/data/undirected/lda_model-50-50.lda')
        )
        self.dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR, 'test/data/undirected/dict.pkl')
        )
        self.interactions = json.load(
            open(os.path.join(CURDIR,
                              'test/data/undirected/interactions.json')))
        
    def test_get_meta_graph_for_undirected_case(self):
        g = IU.get_meta_graph(
            self.interactions,
            undirected=True,
            decompose_interactions=False,
            remove_singleton=False
        )
        assert_equal(827, g.number_of_nodes())
        assert_equal(3874, g.number_of_edges())

    def test_get_topical_meta_graph_for_undirected_case(self):
        # redundant
        g = IU.get_topic_meta_graph(
            self.interactions,
            scipy.stats.entropy,
            self.lda_model,
            self.dictionary,
            undirected=True,
            decompose_interactions=False,
            remove_singleton=False
        )
        assert_equal(827, g.number_of_nodes())
        assert_equal(3874, g.number_of_edges())


class InteractionsUtilTestGivenTopics(unittest.TestCase):
    """when topics are given
    """
    def setUp(self):
        self.interactions = json.load(
            open(os.path.join(CURDIR,
                              'test/data/given_topics/interactions.json')))
        
    def test_get_meta_graph_given_topics(self):
        g = IU.get_meta_graph(
            self.interactions,
            decompose_interactions=False,
            remove_singleton=False,
            given_topics=True,
        )
        assert_equal(297, g.number_of_nodes())
        assert_equal(2325, g.number_of_edges())  # smaller

    def test_get_topical_meta_graph_given_topics(self):
        g = IU.get_topic_meta_graph(
            self.interactions,
            dist_func=euclidean,
            decompose_interactions=False,
            remove_singleton=False,
            given_topics=True,
        )
        assert_equal(297, g.number_of_nodes())
        assert_equal(2325, g.number_of_edges())
        for s, t in g.edges_iter():
            assert_true('c' in g[s][t])
            assert_true(g[s][t]['c'] != float('inf'))
