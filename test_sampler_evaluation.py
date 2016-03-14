import unittest
import networkx as nx
from nose.tools import assert_equal, assert_true
from sampler_evaluation import evaluate, k_max_setcover



class SamplerEvaluationTest(unittest.TestCase):
    def setUp(self):
        t1 = nx.DiGraph()
        t1.add_nodes_from([0, 1])
        t2 = nx.DiGraph()
        t2.add_nodes_from([0, 1, 2])
        t3 = nx.DiGraph()
        t3.add_nodes_from([0, 3, 4])
        self.acc_trees = [t1, t2, t3]
        self.true_trees = []
    
    def test_k_max_setcover(self):
        score = k_max_setcover(self.acc_trees, self.true_trees, k=2)
        assert_equal(5,
                     score)

    def test_evaluate(self):
        self.acc_trees.append(None)
        self.acc_trees.append(None)
        scores = evaluate(self.acc_trees, self.true_trees, k_max_setcover, k=2)
        assert_equal([2, 3, 5, 5, 5], scores)
