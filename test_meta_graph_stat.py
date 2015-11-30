import os
import unittest
import gensim
import ujson as json
from datetime import datetime
from collections import Counter

from nose.tools import assert_equal, assert_true
from .enron_graph import EnronUtil
from .meta_graph_stat import MetaGraphStat

CURDIR = os.path.dirname(os.path.abspath(__file__))


class MetaGraphStatTest(unittest.TestCase):
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

        # some pseudo cost
        for s, t in self.g.edges():
            self.g[s][t]['c'] = 1

        self.s = MetaGraphStat(self.g,
                               kws={
                                   'temporal_traffic': {
                                       'time_resolution': 'hour'
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

    def test_email_count_histogram(self):
        expected = {
            'email_count_hist': Counter({
                (2001, 5, 11, 16, 26, 16): 3,
                (2001, 5, 11, 16, 26, 17): 1,
                (2001, 5, 11, 16, 26, 18): 1,
                (2001, 5, 11, 16, 26, 19): 1,
                (2001, 5, 11, 16, 26, 20): 1,
            })}
        assert_equal(expected,
                     self.s.temporal_traffic(time_resolution='second'))
    
    def test_email_count_histogram_using_hour(self):
        expected = {
            'email_count_hist': Counter({
                (2001, 5, 11, 16): 7
            })}
        assert_equal(expected,
                     self.s.temporal_traffic(time_resolution='hour'))

    def test_summary(self):
        assert_true(isinstance(self.s.summary(), basestring))
