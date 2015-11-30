import os
import unittest
import gensim
import ujson as json
import numpy as np
from datetime import datetime

from nose.tools import assert_equal, assert_true
from .enron_graph import EnronUtil
from .meta_graph_stat import MetaGraphStat

CURDIR = os.path.dirname(os.path.abspath(__file__))


class MetaGraphStatTest(unittest.TestCase):
    def setUp(self):
        self.lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR,
                         'models/model-4-50.lda')
                         # 'test/data/test.lda')
        )
        self.dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR,
                         'models/dictionary.pkl')
                         # 'test/data/test_dictionary.gsm')
        )
        self.interactions = json.load(open(os.path.join(CURDIR,
                                                        'test/data/enron_test.json')))
        
        self.id2msg = {}
        for m in self.interactions:
            self.id2msg[m['message_id']] = "{} {}".format(
                m['subject'], m['body']
            )

        self.g = EnronUtil.get_meta_graph(self.interactions)
        
        # some pseudo cost
        for s, t in self.g.edges():
            self.g[s][t]['c'] = 1

        self.s = MetaGraphStat(self.g,
                               kws={
                                   'temporal_traffic': {
                                       'time_resolution': 'hour'
                                   },
                                   'topics': {
                                       'id2msg': self.id2msg,
                                       'dictionary': self.dictionary,
                                       'lda': self.lda_model,
                                       'top_k': 5
                                   }
                               })

    def test_time_span(self):
        # time zone issue might occur
        expected = {
            'start_time': datetime(2001, 5, 11, 16, 26, 16),
            'end_time': datetime(2001, 5, 11, 16, 26, 20)
        }
        assert_equal(expected, self.s.time_span())
        
    def test_basic_structure_stats(self):
        expected = {
            '#nodes': 7,
            '#singleton': 0,
            '#edges': 10,
            'in_degree': {
                'min': 0,
                'max': 4,
                'average': 1.4285714285714286,
                'median': 1.0
            },
            'out_degree': {
                'min': 0,
                'max': 4,
                'average': 1.4285714285714286,
                'median': 1.0,
            }
        }
        assert_equal(expected,
                     self.s.basic_structure_stats())

    def test_edge_costs(self):
        actual = self.s.edge_costs(max_values=[2, 3])
        for key in ['histogram(<=2)', 'histogram(<=3)']:
            for i in xrange(2):
                np.testing.assert_array_almost_equal(
                    actual['histogram(all)'][i],
                    actual[key][i]
                )
        
    def test_temporal_traffic(self):
        expected = {
            'email_count_hist': [
                ((2001, 5, 11, 16, 26, 16), 3),
                ((2001, 5, 11, 16, 26, 17), 1),
                ((2001, 5, 11, 16, 26, 18), 1),
                ((2001, 5, 11, 16, 26, 19), 1),
                ((2001, 5, 11, 16, 26, 20), 1),
            ]}
        assert_equal(expected,
                     self.s.temporal_traffic(time_resolution='second'))
    
    def test_temporal_traffic_using_hour(self):
        expected = {
            'email_count_hist': [
                ((2001, 5, 11, 16), 7)
            ]}
        assert_equal(expected,
                     self.s.temporal_traffic(time_resolution='hour'))

    def test_topics(self):

        actual = self.s.topics(self.id2msg, self.dictionary, self.lda_model, 5)
        assert_equal(
            (4, ),
            actual['topic_dist'].shape
        )
        assert_true('davis' in
                    actual['topic_terms'])
        assert_true('utilities' in
                    actual['topic_terms'])
        
    def test_summary(self):
        s = self.s.summary()
        assert_true(isinstance(s, basestring))
        assert_true('email_count_hist' in s)
        assert_true('topic_dist' in s)
        assert_true('topic_terms' in s)
