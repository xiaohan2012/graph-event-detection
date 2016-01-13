import os
import unittest
import pandas as pd
import numpy as np
import cPickle as pkl
from nose.tools import assert_equal, assert_true, assert_almost_equal
from sklearn import metrics

from .synthetic_evaluation import group_paths, evaluate_U,\
    get_values_by_key
from .test_util import make_path
from .util import load_items_by_line, json_load
from .max_cover import k_best_trees
from .evaluation import evaluate_meta_tree_result


class SyntheticEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.paths_U = map(
            make_path,
            load_items_by_line(
                make_path("test/data/synthetic/result_paths_U.txt")
            )
        )
        self.filter_paths = (lambda paths, pattern:
                             [p for p in paths
                              if pattern in os.path.basename(p)])

    def test_group_paths(self):
        groups = [
            (('lst', 'True'), sorted(
                self.filter_paths(self.filter_paths(self.paths_U, 'lst'),
                                  'dijkstra=True'))),
            (('lst', 'False'), sorted(
                self.filter_paths(self.filter_paths(self.paths_U, 'lst'),
                                  'dijkstra=False'))),
            (('greedy', 'False'), sorted(
                self.filter_paths(self.paths_U, 'greedy'))),
            (('random', 'False'), sorted(
                self.filter_paths(self.paths_U, 'random'))),
            (('variance', 'False'), sorted(
                self.filter_paths(self.paths_U, 'variance'))),
        ]
        print(len(self.filter_paths(self.filter_paths(self.paths_U, 'lst'),
                                    'dijkstra=False')))
        assert_equal(
            sorted(groups),
            group_paths(
                self.paths_U,
                keyfunc=lambda p: (p['args'][0], p['dijkstra'])
            )
        )
        
    def test_evaluate_U(self):
        interactions_path = make_path(
            'test/data/synthetic/interactions.json'
        )
        events_path = make_path('test/data/synthetic/events.json')
        actual = evaluate_U(
            self.paths_U,
            interactions_path=interactions_path,
            events_path=events_path,
            metrics=[metrics.adjusted_rand_score],
            K=10
        )
        for key in ('recall', 'precision', 'f1', 'adjusted_rand_score'):
            assert_true(key in actual)
            assert_true(
                isinstance(actual[key], pd.DataFrame)
            )
            np.testing.assert_almost_equal(
                np.linspace(0.1, 1, num=10),
                actual[key].columns
            )
            for method in ('lst-dij', 'greedy'):
                assert_true(method in actual[key].index)

        pred_trees = k_best_trees(
            pkl.load(
                open(
                    make_path(
                        "test/data/synthetic/result-lst-dijkstra=True--U=0.6.pkl"
                    ))), 10)
        interactions = json_load(interactions_path)
        assert_almost_equal(
            evaluate_meta_tree_result(
                json_load(events_path),
                pred_trees,
                [i['message_id'] for i in interactions],
                [metrics.adjusted_rand_score])['f1'],
            actual['f1'].loc['lst-dij', 0.6]
        )

    def test_get_values_by_key(self):
        np.testing.assert_almost_equal(
            np.linspace(0.1, 1, num=10).tolist(),
            np.array(
                get_values_by_key(
                    sorted(self.filter_paths(self.paths_U, 'greedy')),
                    key='U',
                    map_func=float)
            )
        )
