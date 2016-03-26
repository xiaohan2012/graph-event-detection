import os
import unittest
import pandas as pd
import numpy as np
import cPickle as pkl
from nose.tools import assert_equal, assert_true, assert_almost_equal
from sklearn import metrics

from .synthetic_evaluation import group_paths, evaluate_against_noise,\
    get_values_by_key
from .test_util import make_path
from .util import load_items_by_line, json_load
from .max_cover import k_best_trees
from .evaluation import evaluate_meta_tree_result
from .experiment_util import parse_result_path


class SyntheticEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.paths_U = map(
            make_path,
            load_items_by_line(
                make_path("test/data/synthetic/result_paths_U.txt")
            )
        )
        self.result_paths_single_tree = map(
            lambda p: make_path('test/data/synthetic_single_tree/result', p),
            load_items_by_line(
                make_path("test/data/synthetic_single_tree/result_paths_single_tree.txt")
            )
        )
        self.paths_preprune_seconds = map(
            make_path,
            load_items_by_line(
                make_path(
                    "test/data/synthetic/result_paths_preprune_seconds.txt"
                )
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
        assert_equal(
            sorted(groups),
            group_paths(
                self.paths_U,
                keyfunc=lambda p: (p['args'][0], p['dijkstra'])
            )
        )
        
    def test_group_paths_with_sort_key(self):
        actual = group_paths(
            self.paths_preprune_seconds,
            keyfunc=lambda p: 'nothing',
            sort_keyfunc=lambda param: int(param['preprune_secs'])
        )
        assert_equal(1, len(actual))
        assert_equal('nothing', actual[0][0])
        np.testing.assert_almost_equal(
            np.linspace(2, 30, num=15),
            [int(parse_result_path(p)['preprune_secs'])
             for p in actual[0][1]]
        )

    def test_evaluate_against_noise(self):
        make_single_tree_path = (lambda p:
                                 make_path(
                                     'test/data/synthetic_single_tree/', p)
        )
        interactions_paths = ['interactions--n_noisy_interactions_fraction=0.2.json',
                             'interactions--n_noisy_interactions_fraction=0.4.json']
        interactions_paths = sorted(map(make_single_tree_path, interactions_paths) * 2)
        events_paths = ['events--n_noisy_interactions_fraction=0.2.pkl',
                       'events--n_noisy_interactions_fraction=0.4.pkl']
        events_paths = sorted(map(make_single_tree_path, events_paths) * 2)

        actual = evaluate_against_noise(
            result_paths=self.result_paths_single_tree,
            interactions_paths=interactions_paths,
            events_paths=events_paths,
            metrics=[metrics.adjusted_rand_score],
            xticks=[]
        )
        for key in ('recall', 'precision', 'f1',
                    'adjusted_rand_score'):
            # each key => dataframe
            assert_true(key in actual)
            assert_true(
                isinstance(actual[key], pd.DataFrame)
            )
            # check x axis
            np.testing.assert_almost_equal(
                np.asarray([0.2, 0.4]),
                actual[key].columns
            )
            # check the legend part
            for method in ('random', 'greedy'):
                assert_true(method in actual[key].index)

        # check if the score is right
        pred_trees = pkl.load(open(make_single_tree_path(
            'result/result--fraction=0.2--greedy--U=34.0728347028--dijkstra=False--timespan=100.28206487----apply_pagerank=False--dist_func=cosine--distance_weights={"topics":1.0}--preprune_secs=100.28206487----cand_tree_percent=0.1--root_sampling=uniform.pkl'
        )))
        true_trees = pkl.load(open(make_single_tree_path(
            "events--n_noisy_interactions_fraction=0.2.pkl"
        )))
        interactions = json_load(interactions_paths[0])
        expected_f1 = evaluate_meta_tree_result(
            true_trees,
            pred_trees,
            [i['message_id'] for i in interactions],
            methods=[])['f1']
        actual_f1 = actual['f1'].loc['greedy', 0.2]

        assert_almost_equal(
            expected_f1,
            actual_f1
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
