import unittest
import numpy as np
from nose.tools import assert_equal, assert_almost_equal
from sklearn import metrics
from .evaluation import precision_recall_f1, \
    convert_to_cluster_assignment_array, \
    evaluate_clustering_result


class EvaluationTest(unittest.TestCase):
    def setUp(self):
        self.all_entry_ids = range(10)
        self.true_clusters = [[6, 7, 4, 5], [0, 1]]
        self.pred_clusters = [[5, 7, 8], [0, 1]]
        self.args = (self.true_clusters,
                     self.pred_clusters,
                     self.all_entry_ids)

    def test_precision_recall_f1(self):
        p, r, f1 = precision_recall_f1(self.true_clusters,
                                       self.pred_clusters)
        assert_almost_equal(0.8, p)
        assert_almost_equal(2 / 3., r)
        assert_almost_equal(8 / 11., f1)
        
    def test_convert_to_cluster_assignment_array_all_data(self):
        true_assignment, pred_assignment = convert_to_cluster_assignment_array(
            self.true_clusters,
            self.pred_clusters,
            self.all_entry_ids,
            true_only=False
        )
        np.testing.assert_array_almost_equal(
            np.array([2, 2, 0, 0, 1, 1, 1, 1, 0, 0]),
            true_assignment
        )
        np.testing.assert_array_almost_equal(
            np.array([2, 2, 0, 0, 0, 1, 0, 1, 1, 0]),
            pred_assignment
        )    

    def test_convert_to_cluster_assignment_array(self):
        true_assignment, pred_assignment = convert_to_cluster_assignment_array(
            self.true_clusters,
            self.pred_clusters,
            self.all_entry_ids,
            true_only=True
        )
        np.testing.assert_array_almost_equal(
            np.array([2, 2, 1, 1, 1, 1]),
            true_assignment
        )
        np.testing.assert_array_almost_equal(
            np.array([2, 2, 0, 1, 0, 1]),
            pred_assignment
        )
        
    def test_evaluate_clustering_result_true_only(self):
        assert_almost_equal(
            metrics.adjusted_rand_score(
                [2, 2, 1, 1, 1, 1],
                [2, 2, 0, 1, 0, 1]
            ),
            evaluate_clustering_result(
                self.true_clusters,
                self.pred_clusters,
                self.all_entry_ids,
                metric=metrics.adjusted_rand_score,
                true_only=True
            )
        )
        
    def test_evaluate_clustering_result(self):
        assert_almost_equal(
            metrics.adjusted_mutual_info_score(
                [2, 2, 0, 0, 1, 1, 1, 1, 0, 0],
                [2, 2, 0, 0, 0, 1, 0, 1, 1, 0]
            ),
            evaluate_clustering_result(
                self.true_clusters,
                self.pred_clusters,
                self.all_entry_ids,
                metric=metrics.adjusted_mutual_info_score,
                true_only=False
            )
        )
