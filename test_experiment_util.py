
import unittest
import networkx as nx
import os
import numpy as np
import glob
import cPickle as pkl

from nose.tools import assert_equal, assert_true

from datetime import timedelta

from .experiment_util import sample_rooted_binary_graphs_within_timespan


CURDIR = os.path.dirname(os.path.abspath(__file__))


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
            assert_true(isinstance(t, nx.DiGraph))

    def tearDown(self):
        for p in glob.glob(os.path.join(CURDIR, 'test/data/tmp/*')):
            os.remove(p)
