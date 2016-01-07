import unittest
import random
import networkx as nx
import os
import numpy as np
import glob
import cPickle as pkl

from nose.tools import assert_equal, assert_true
from collections import Counter
from datetime import timedelta

from .experiment_util import sample_rooted_binary_graphs_within_timespan,\
    experiment_signature,\
    sample_nodes_by_weight,\
    sample_nodes_by_out_degree


CURDIR = os.path.dirname(os.path.abspath(__file__))


def test_experiment_signature():
    assert_equal("", experiment_signature())
    assert_equal("a=1--b=two--c=True--d=1.5--e=asarray--f=28days",
                 experiment_signature(a=1, b='two', c=True, d=1.5,
                                      e=np.asarray, f=timedelta(weeks=4)))
    

class ExperimentUtilTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(123456)

    def test_sample_rooted_binary_graphs_within_timespan(self):
        output_path = os.path.join(CURDIR, 'test/data/tmp/samples.pkl')
    
        sample_rooted_binary_graphs_within_timespan(
            meta_graph_pickle_path=os.path.join(
                CURDIR,
                'test/data/enron-head-100.pkl'),
            sample_number=10,
            timespan=timedelta(weeks=4).total_seconds(),
            output_path=output_path
        )
        
        trees = pkl.load(open(output_path))
        assert_equal(6, len(trees))
        for t in trees:
            for n in t.nodes():
                assert_true(len(t.neighbors(n)) <= 2)

    def tearDown(self):
        for p in glob.glob(os.path.join(CURDIR, 'test/data/tmp/*')):
            os.remove(p)


def test_sample_nodes_by_weight():
    random.seed(123456)
    g = nx.DiGraph()
    g.add_node(0, w=100)
    g.add_node(1, w=10)
    g.add_node(2, w=1)

    w_func = lambda n: g.node[n]['w']
    for i in xrange(1, 4):
        assert_equal(
            range(i), sample_nodes_by_weight(g, w_func, i)
        )
    assert_equal(
        range(3), sample_nodes_by_weight(g, w_func, 100)
    )


def test_sample_nodes_by_out_degree():
    random.seed(123456)
    g = nx.DiGraph()
    n = 5
    for i in xrange(n):
        for j in xrange(i+1, n):
            g.add_edge(i, j)

    all_results = []
    for i in xrange(1000):
        all_results += sample_nodes_by_out_degree(g, 1)

    cnt = Counter(all_results)
    
    assert_equal(399, cnt[0])
    assert_equal(293, cnt[1])
    assert_equal(197, cnt[2])
    assert_equal(111, cnt[3])
    assert_equal(0, cnt[4])
