import random
import os
import unittest
import glob
import numpy
import cPickle as pkl

from datetime import timedelta
from nose.tools import assert_equal, assert_true

from gen_candidate_trees import run
from .lst import lst_dag
from .baselines import greedy_grow, random_grow

CURDIR = os.path.dirname(os.path.abspath(__file__))


class GenCandidateTreeTest(unittest.TestCase):
    def setUp(self):
        random.seed(123456)
        numpy.random.seed(123456)
    
        self.some_kws_of_run = {
            'timespan': timedelta(weeks=2).total_seconds(),  # 1 month
            'enron_json_path': os.path.join(CURDIR,
                                            'test/data/enron-head-100.json'),
            'lda_model_path': os.path.join(CURDIR, 'test/data/test.lda'),
            'corpus_dict_path': os.path.join(CURDIR,
                                             'test/data/test_dictionary.gsm'),
            'enron_pkl_path': os.path.join(CURDIR,
                                           'test/data/enron-head-100.pkl'),
            'cand_tree_number': 5
        }
        self.lst = lambda g, r, U: lst_dag(
            g, r, U,
            edge_weight_decimal_point=2,
            debug=False
        )

    def _calc_enron_pkl(self):
        run(
            self.lst,
            calculate_graph=True,
            debug=True,
            print_summary=True,
            result_pkl_path=os.path.join(CURDIR, 'test/data/tmp/test.pkl'),
            **self.some_kws_of_run
        )
        
    def check(self, test_name, tree_gen_func, expected_tree_number):
        # empty trees are ignored
        # thus, the actual tree number should <= expected_tree_number
        pickle_path = os.path.join(CURDIR,
                                   "test/data/tmp",
                                   "{}.pkl".format(test_name))
        run(tree_gen_func,
            calculate_graph=False,
            print_summary=False,
            result_pkl_path=pickle_path,
            **self.some_kws_of_run)

        trees = pkl.load(open(pickle_path))
        print(trees)
        assert_equal(expected_tree_number, len(trees))
        for t in trees:
            assert_true(len(t.edges()) > 0)

    def test_greedy_grow(self):
        self.check('greedy', greedy_grow, 2)

    def test_random_grow(self):
        self.check('random', random_grow, 2)

    def test_lst_dag(self):
        self.check('lst', self.lst, 2)

    def tearDown(self):
        # remove the pickles
        files = glob.glob(os.path.join(CURDIR,
                                       "test/data/tmp/*"))
        for f in files:
            os.remove(f)
