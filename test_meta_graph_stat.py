import os
import unittest
import gensim
import ujson as json
from datetime import datetime

from nose.tools import assert_equal
from .enron_graph import EnronUtil
from .stat import MetaGraphStat

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
        self.s = MetaGraphStat(self.g)

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
