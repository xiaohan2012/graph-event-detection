import os
import unittest
import gensim
import ujson as json
import numpy as np
from datetime import datetime

from nose.tools import assert_equal, assert_true, assert_almost_equal
from .util import load_json_by_line
from .interactions import InteractionsUtil as IU
from .meta_graph_stat import MetaGraphStat

CURDIR = os.path.dirname(os.path.abspath(__file__))


class MetaGraphStatTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(123456)
        self.lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR,
                         'test/data/test.lda')
        )
        self.dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR,
                         'test/data/test_dictionary.gsm')
        )
        self.interactions = IU.clean_interactions(
            json.load(
                open(os.path.join(CURDIR, 'test/data/enron_test.json'))
            )
        )

        self.people_info = load_json_by_line(
            os.path.join(CURDIR, 'test/data/people.json')
        )

        self.g = IU.get_meta_graph(self.interactions,
                                   remove_singleton=True)

        # some pseudo cost
        for s, t in self.g.edges():
            self.g[s][t]['c'] = 1

        self.s = MetaGraphStat(self.g,
                               kws={
                                   'temporal_traffic': {
                                       'time_resolution': 'hour'
                                   },
                                   'topics': {
                                       'interactions': self.interactions,
                                       'dictionary': self.dictionary,
                                       'lda': self.lda_model,
                                       'top_k': 5
                                   },
                                   'email_content': {
                                       'interactions': self.interactions
                                   },
                                   'participants': {
                                       'people_info': self.people_info,
                                       'interactions': self.interactions
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
            },
            'roots': sorted(['1.B', '1.C', '1.D'])
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
        actual = self.s.topics(self.interactions,
                               self.dictionary,
                               self.lda_model,
                               5)
        assert_equal(
            (4, ),
            actual['topic_dist'].shape
        )
        assert_true('davis' in
                    actual['topic_terms'])
        assert_true('utilities' in
                    actual['topic_terms'])

        assert_almost_equal(0.105, actual['topic_divergence'], places=3)
        
    def test__topic_divergence(self):
        id2msg = {}
        for m in self.interactions:
            id2msg[m['message_id']] = "{} {}".format(
                m['subject'], m['body']
            )
        msg_ids = [self.s.g.node[n]['message_id']
                   for n in self.s.g.nodes()]
        actual = self.s._topic_divergence(msg_ids, id2msg,
                                          self.dictionary,
                                          self.lda_model)
        assert_almost_equal(0.106, actual, places=3)
        
    def test_email_content(self):
        actual = self.s.email_content(self.interactions, 1, unique=False)
        assert_equal(actual['subjects(top1)'], ['s1'])

    def test_email_content_without_duplicates(self):
        actual = self.s.email_content(self.interactions,
                                      top_k=1000,
                                      unique=True)
        assert_equal(sorted(actual['subjects(top1000)']),
                     sorted(['s1', '', '...']))

    def test_participants(self):
        # Note: we are operating on decomposed interactions
        actual = self.s.participants(self.people_info, self.interactions,
                                     top_k=5)
        assert_equal(actual['sender_count'],
                     [(('A', 'A@enron.com'), 5),
                      (('D', 'D@enron.com'), 2)])
        assert_equal(actual['recipient_count'],
                     [(('B', 'B@enron.com'), 4),
                      (('D', 'D@enron.com'), 3),
                      (('C', 'C@enron.com'), 3),
                      (('F', 'F@enron.com'), 2),
                      (('E', 'E@enron.com'), 1)])
        assert_equal(actual['participant_count'],
                     [(('D', 'D@enron.com'), 5),
                      (('A', 'A@enron.com'), 5),
                      (('B', 'B@enron.com'), 4),
                      (('C', 'C@enron.com'), 3),
                      (('F', 'F@enron.com'), 2)])
        assert_almost_equal(0.598, actual['sender_entropy'], places=3)
        assert_true('recipient_entropy' in actual)
        assert_true('participant_entropy' in actual)

    def test_summary(self):
        s = self.s.summary()
        assert_true(isinstance(s, basestring))
        assert_true('email_count_hist' in s)
        assert_true('topic_dist' in s)
        assert_true('topic_terms' in s)
        assert_true('subjects(top' in s)
        assert_true('participant_count' in s)
        
    def test_disable_method(self):
        s = MetaGraphStat(self.g,
                          kws={
                              'temporal_traffic': False,
                              'topics': {
                                  'interactions': self.interactions,
                                  'dictionary': self.dictionary,
                                  'lda': self.lda_model,
                                  'top_k': 5
                              },
                              'email_content': {
                                  'interactions': self.interactions
                              },
                              'participants': False
                          })

        summary = s.summary()
        assert_true(isinstance(summary, basestring))
        assert_true('email_count_hist' not in summary)
        assert_true('topic_dist' in summary)
        assert_true('topic_terms' in summary)
        assert_true('subjects(top' in summary)
        assert_true('participant_count' not in summary)
