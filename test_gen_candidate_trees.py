import random
import os
import unittest
import numpy
import cPickle as pkl

from datetime import timedelta
from nose.tools import assert_true
from subprocess import check_output

from gen_candidate_trees import run
from scipy.stats import entropy

from .lst import lst_dag, dp_dag_general, make_variance_cost_func
from .baselines import greedy_grow, random_grow
from .test_util import remove_tmp_data, CURDIR


class GenCandidateTreeTest(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)
    
        self.some_kws_of_run = {
            'interaction_json_path': os.path.join(
                CURDIR,
                'test/data/enron-head-100.json'),
            'lda_model_path': os.path.join(CURDIR, 'test/data/test.lda'),
            'corpus_dict_path': os.path.join(CURDIR,
                                             'test/data/test_dictionary.gsm'),
            'meta_graph_pkl_path_prefix': os.path.join(
                CURDIR,
                'test/data/enron-head-100'),
            'cand_tree_number': 5,
            'meta_graph_kws': {
                'dist_func': entropy,
                'decompose_interactions': False,
                'preprune_secs': timedelta(weeks=4)
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

        self.variance_method = lambda g, r, U: dp_dag_general(
            g, r, int(U*10),  # fixed point 1
            make_variance_cost_func(entropy, 'topics',
                                    fixed_point=1,
                                    debug=True),
            debug=False
        )

        self.meta_pickle_path_common = "decompose_interactions=False--dist_func=entropy--preprune_secs=28days"
        pkl_path = os.path.join(
            CURDIR,
            'test/data/enron-head-100--{}.pkl'.format(
                self.meta_pickle_path_common)
        )
        if not os.path.exists(pkl_path):
            print('calc meta graph')
            self._calc_cand_trees_pkl()
        else:
            print('no need to calc meta graph')

    def _calc_cand_trees_pkl(self):
        run(
            self.lst,
            calculate_graph=True,
            debug=False,
            print_summary=False,
            result_pkl_path_prefix=os.path.join(
                CURDIR,
                'test/data/tmp/test'),  # can be ignored
            **self.some_kws_of_run
        )

    def check(self, test_name, tree_gen_func):
        # empty trees are ignored
        # very likely actual tree number should >= 0
        result_pickle_prefix = os.path.join(CURDIR,
                                            "test/data/tmp",
                                            "result-{}".format(test_name))

        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=28days----%s' %(
            self.meta_pickle_path_common
        )

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

        assert_true(len(trees) > 0)
        for t in trees:
            assert_true(len(t.edges()) > 0)
        return trees

    def test_if_sender_and_recipient_information_saved(self):
        trees = self.check('lst', self.lst)
        for t in trees:
            for n in t.nodes():
                assert_true('sender_id' in t.node[n])
                assert_true('recipient_ids' in t.node[n])
        
    def test_greedy_grow(self):
        self.check('greedy', greedy_grow)

    def test_random_grow(self):
        self.check('random', random_grow)

    def test_lst_dag(self):
        self.check('lst', self.lst)

    def test_lst_dag_after_dijkstra(self):
        trees = self.check('lst', self.lst)

        self.some_kws_of_run['gen_tree_kws']['dijkstra'] = True
        trees_with_dij = self.check('lst', self.lst)

        for t, t_dij in zip(trees, trees_with_dij):
            assert_true(sorted(t.edges()) != sorted(t_dij))

    def test_variance_method(self):
        self.check('variance', self.variance_method)

    def tearDown(self):
        remove_tmp_data('test/data/tmp/*')


class GenCandidateTreeCMDTest(unittest.TestCase):
    """test for commandline
    """
    def setUp(self):
        random.seed(123456)
        numpy.random.seed(123456)

        self.script_path = os.path.join(CURDIR, "gen_candidate_trees.py")
        self.result_dir = os.path.join(CURDIR, "test/data/tmp")
        self.lda_path = os.path.join(CURDIR, "test/data/test.lda")
        self.interaction_json_path = os.path.join(
            CURDIR,
            'test/data/enron-head-100.json')
        self.corpus_dict_path = os.path.join(
            CURDIR,
            'test/data/test_dictionary.gsm')
        self.meta_graph_path_prefix = os.path.join(
            CURDIR,
            'test/data/enron-head-100')

    def check(self, method="random", distance="entropy",
              sampling_method="uniform", extra=""):
        cmd = """python {} \
        --method={} \
        --dist={} \
        --cand_n=1 \
        --root_sampling={}\
        --res_dir={} --weeks=4 --U=0.5 \
        --lda_path={} --interaction_path={} \
        --corpus_dict_path={} \
        --meta_graph_path_prefix={} \
        {}""".format(
            self.script_path,
            method, distance,
            sampling_method,
            self.result_dir,
            self.lda_path,
            self.interaction_json_path,
            self.corpus_dict_path,
            self.meta_graph_path_prefix,
            extra
        ).split()
        output = check_output(cmd)
        assert_true("traceback" not in output.lower())
        print(output)
        output_path = os.path.join(
            CURDIR,
            "test/data/tmp/result-{}--U=0.5--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func={}--preprune_secs=28days.pkl".format(method, distance)
        )
        assert_true(os.path.exists(output_path))
        return output

    def test_random(self):
        self.check(method='random')

    def test_variance(self):
        self.check(method='variance')

    def test_out_degree_sampling(self):
        output = self.check(sampling_method='out_degree')
        assert_true('out_degree' in output)
        
    def tearDown(self):
        remove_tmp_data('test/data/tmp')
