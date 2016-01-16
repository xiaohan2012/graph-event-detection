import unittest
import networkx as nx
from nose.tools import assert_equal, assert_raises, \
    assert_true
from .util import json_load
from .test_util import make_path
from hig import construct_hig_from_interactions
from interactions import InteractionsUtil as IU


class HIGTest(unittest.TestCase):
    def setUp(self):
        self.interactions = IU.clean_interactions(
            json_load(
                make_path('test/data/enron_test.json')
            )
        )

    def test_construct_hig(self):
        hig = construct_hig_from_interactions(
            self.interactions
        )
        a, b, c, d, e, f = ('A', 'B', 'C', 'D', 'E', 'F')
        assert_equal(
            sorted(
                range(1, 6) +
                [a, b, c, d, e, f]
            ),
            sorted(hig.nodes()))
        assert_equal(
            sorted(
                [(a, 1), (1, b), (1, c), (1, d),
                 (a, 2), (2, f),
                 (d, 3), (3, e),
                 (a, 4), (4, b),
                 (d, 5), (5, f),
             ]),
            sorted(hig.edges())
        )

    def test_construct_hig_interacting_ids(self):
        self.interactions.append({'sender_id': 1,
                                  'recipient_ids': [1],
                                  'message_id': 7})
        assert_raises(ValueError,
                      construct_hig_from_interactions,
                      self.interactions)

    def test_pagerank_on_hig(self):
        pr = nx.pagerank(construct_hig_from_interactions(
            self.interactions
        ))
        assert_true(pr['A'] < pr['F'])
        
