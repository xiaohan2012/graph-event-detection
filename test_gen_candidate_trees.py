import random
import os
import unittest
import numpy
import cPickle as pkl

from datetime import timedelta
from nose.tools import assert_equal, assert_true
from subprocess import check_output

from gen_candidate_trees import run
from scipy.stats import entropy

from .lst import lst_dag
from .baselines import greedy_grow, random_grow
from .test_util import remove_tmp_data, CURDIR


class GenCandidateTreeTest(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)
    
        self.some_kws_of_run = {
            'enron_json_path': os.path.join(CURDIR,
                                            'test/data/enron-head-100.json'),
            'lda_model_path': os.path.join(CURDIR, 'test/data/test.lda'),
            'corpus_dict_path': os.path.join(CURDIR,
                                             'test/data/test_dictionary.gsm'),
            'enron_pkl_path_prefix': os.path.join(CURDIR,
                                                  'test/data/enron-head-100'),
            'cand_tree_number': 5,
            'meta_graph_kws': {
                'dist_func': entropy,
                'decompose_interactions': False
            },
            'gen_tree_kws': {
                'timespan': timedelta(weeks=4),
                'U': 0.5,
                'dijkstra': False
            }
        }
        self.lst = lambda g, r, U: lst_dag(
            g, r, U,
            edge_weight_decimal_point=2,
            debug=False
        )
        pkl_path = os.path.join(
            CURDIR,
            'test/data/enron-head-100--decompose_interactions=False--dist_func=entropy.pkl'
        )
        if not os.path.exists(pkl_path):
            print('calc meta graph')
            self._calc_enron_pkl()

    def _calc_enron_pkl(self):
        run(
            self.lst,
            calculate_graph=True,
            debug=False,
            print_summary=False,
            result_pkl_path_prefix=os.path.join(CURDIR, 'test/data/tmp/test'),  # can be ignored
            **self.some_kws_of_run
        )        
    
    def check(self, test_name, tree_gen_func, expected_tree_number):
        # empty trees are ignored
        # thus, the actual tree number should <= expected_tree_number
        result_pickle_prefix = os.path.join(CURDIR,
                                            "test/data/tmp",
                                            "result-{}".format(test_name))

        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=28days----decompose_interactions=False--dist_func=entropy'

        if self.some_kws_of_run['gen_tree_kws'].get('dijkstra'):
            pickle_path_suffix = pickle_path_suffix.format("True")
        else:
            pickle_path_suffix = pickle_path_suffix.format("False")

        pickle_path = "{}--{}.pkl".format(
            result_pickle_prefix,
            pickle_path_suffix
        )

        run(tree_gen_func,
            calculate_graph=False,
            print_summary=False,
            result_pkl_path_prefix=result_pickle_prefix,
            **self.some_kws_of_run)

        trees = pkl.load(open(pickle_path))

        assert_equal(expected_tree_number, len(trees))
        for t in trees:
            assert_true(len(t.edges()) > 0)
        return trees

    def test_if_sender_and_recipient_information_saved(self):
        trees = self.check('lst', self.lst, 2)
        for t in trees:
            for n in t.nodes():
                assert_true('sender_id' in t.node[n])
                assert_true('recipient_ids' in t.node[n])
        
    def test_greedy_grow(self):
        self.check('greedy', greedy_grow, 2)

    def test_random_grow(self):
        self.check('random', random_grow, 1)

    def test_lst_dag(self):
        self.check('lst', self.lst, 2)

    def test_lst_dag_after_dijkstra(self):
        trees = self.check('lst', self.lst, 2)

        self.some_kws_of_run['gen_tree_kws']['dijkstra'] = True
        trees_with_dij = self.check('lst', self.lst, 5)

        for t, t_dij in zip(trees, trees_with_dij):
            assert_true(sorted(t.edges()) != sorted(t_dij))

    def tearDown(self):
        remove_tmp_data('test/data/tmp/*')


class GenCandidateTreeCMDTest(unittest.TestCase):
    """test for commandline
    """
    def setUp(self):
        random.seed(123456)
        numpy.random.seed(123456)

    def test_simple(self):
        script_path = os.path.join(CURDIR, "gen_candidate_trees.py")
        result_dir = os.path.join(CURDIR, "test/data/tmp")
        cmd = "python {} --method=random --dist=entropy --cand_n=1 --res_dir={} --weeks=4 --U=0.5 --lda=models/model-4-50.lda".format(
            script_path, result_dir
        ).split()
        output = check_output(cmd)
        print(output)
        assert_true("traceback" not in output.lower())
        
        output_path = os.path.join(CURDIR,
                                   "test/data/tmp/result-random--U=0.5--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func=entropy.pkl")
        assert_true(os.path.exists(output_path))

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
