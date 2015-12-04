
import unittest
import networkx as nx
import os
import numpy as np
import glob
import cPickle as pkl

from nose.tools import assert_equal, assert_true

from datetime import timedelta

from .experiment_util import (sample_rooted_binary_graphs_within_timespan,
                              experiment_signature)


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


        
