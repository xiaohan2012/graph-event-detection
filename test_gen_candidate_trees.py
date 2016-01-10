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
from scipy.spatial.distance import euclidean

from .lst import lst_dag, dp_dag_general, make_variance_cost_func
from .baselines import greedy_grow, random_grow
from .test_util import remove_tmp_data, make_path, CURDIR


directed_params = {
    'interaction_json_path': make_path('test/data/enron-head-100.json'),
    'lda_model_path': make_path('test/data/test.lda'),
    'corpus_dict_path': make_path('test/data/test_dictionary.gsm'),
    'meta_graph_pkl_path_prefix': make_path('test/data/enron-head-100'),
    'undirected': False
}

undirected_params = {
    'interaction_json_path': make_path(
        'test/data/undirected/interactions.json'
    ),
    'lda_model_path': make_path(
        'test/data/undirected/lda_model-50-50.lda'
    ),
    'corpus_dict_path': make_path(
        'test/data/undirected/dict.pkl'
    ),
    'meta_graph_pkl_path_prefix': make_path(
        'test/data/undirected/meta-graph'
    ),
    'undirected': True
}


lst = lambda g, r, U: lst_dag(
    g, r, U,
    edge_weight_decimal_point=2,
    debug=False
)

variance_method = lambda g, r, U: dp_dag_general(
    g, r, int(U*10),  # fixed point 1
    make_variance_cost_func(entropy, 'topics',
                            fixed_point=1,
                            debug=False),
    debug=False
)

variance_method_euclidean = lambda g, r, U: dp_dag_general(
    g, r, int(U*10),  # fixed point 1
    make_variance_cost_func(euclidean,
                            'topics',
                            fixed_point=1,
                            debug=False),
    debug=False
)


class GenCandidateTreeTest(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)

        self.some_kws_of_run = {
            'cand_tree_number': 5,
            'meta_graph_kws': {
                'dist_func': entropy,
                'decompose_interactions': False,
                'preprune_secs': timedelta(weeks=4).total_seconds()
            },
            'gen_tree_kws': {
                'timespan': timedelta(weeks=4).total_seconds(),
                'U': 0.5,
                'dijkstra': False
            }
        }

        self.meta_pickle_path_common = "decompose_interactions=False--dist_func=entropy--preprune_secs=28days"
        pkl_path = make_path('test/data/enron-head-100--{}.pkl'.format(
            self.meta_pickle_path_common)
        )
        if not os.path.exists(pkl_path):
            print('calc meta graph')
            self._calc_cand_trees_pkl(undirected=False)
            self._calc_cand_trees_pkl(undirected=True)
        else:
            print('no need to calc meta graph')

    def _calc_cand_trees_pkl(self, undirected):
        kws = self.some_kws_of_run.copy()
        print(undirected)
        if undirected:
            kws.update(undirected_params)
        else:
            kws.update(directed_params)

        run(
            lst,
            calculate_graph=True,
            debug=False,
            print_summary=False,
            result_pkl_path_prefix=make_path('test/data/tmp/test'),  # can be ignored
            **kws
        )

    def check(self, test_name, tree_gen_func, undirected=False, **more_args):
        # empty trees are ignored
        # very likely actual tree number should >= 0
        result_pickle_prefix = make_path("test/data/tmp",
                                         "result-{}".format(test_name))
        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=28days----%s' %(
            self.meta_pickle_path_common
        )
        kws = self.some_kws_of_run.copy()
        
        if undirected:
            kws.update(undirected_params)
        else:
            kws.update(directed_params)
        
        if more_args:
            kws.update(more_args)

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
            **kws)

        trees = pkl.load(open(pickle_path))

        assert_true(len(trees) > 0)
        for t in trees:
            assert_true(len(t.edges()) > 0)
        return trees

    def test_if_sender_and_recipient_information_saved(self):
        trees = self.check('lst', lst)
        for t in trees:
            for n in t.nodes():
                assert_true('sender_id' in t.node[n])
                assert_true('recipient_ids' in t.node[n])
        
    def test_greedy_grow(self):
        self.check('greedy', greedy_grow)

    def test_random_grow(self):
        self.check('random', random_grow)

    def test_lst_dag(self):
        self.check('lst', lst)

    def test_lst_dag_after_dijkstra(self):
        trees = self.check('lst', lst)

        self.some_kws_of_run['gen_tree_kws']['dijkstra'] = True
        trees_with_dij = self.check('lst', lst)

        for t, t_dij in zip(trees, trees_with_dij):
            assert_true(sorted(t.edges()) != sorted(t_dij))

    def test_variance_method(self):
        self.check('variance', variance_method)

    def test_undirected(self):
        self.check('variance', variance_method,
                   undirected=True)

    def tearDown(self):
        remove_tmp_data('test/data/tmp/*')


class GenCandidateTreeCMDTest(unittest.TestCase):
    """test for commandline
    """
    def setUp(self):
        random.seed(123456)
        numpy.random.seed(123456)

        self.script_path = make_path("gen_candidate_trees.py")
        self.result_dir = make_path("test/data/tmp")

        self.directed_result_output_path_template = "test/data/tmp/result-{}--U=0.5--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func={}--preprune_secs=28days.pkl"
        self.undirected_result_output_path_template = "test/data/tmp/result-{}--U=0.5--dijkstra=False--timespan=28days----decompose_interactions=False--dist_func={}--preprune_secs=28days.pkl"

    def check(self, method="random", distance="entropy",
              sampling_method="uniform", extra="", undirected=False):
        if undirected:
            more_params = undirected_params
        else:
            more_params = directed_params

        cmd = """python {} \
        --method={method} \
        --dist={distance_func} \
        --cand_n=1 \
        --root_sampling={sampling_method}\
        --res_dir={result_dir} --weeks=4 --U=0.5 \
        --lda_path={lda_model_path} --interaction_path={interaction_json_path} \
        --corpus_dict_path={corpus_dict_path} \
        --meta_graph_path_prefix={meta_graph_pkl_path_prefix} \
        {extra}""".format(
            self.script_path,
            method=method,
            distance_func=distance,
            sampling_method=sampling_method,
            result_dir=self.result_dir,
            extra=extra,
            **more_params
        ).split()
        output = check_output(cmd)
        assert_true("traceback" not in output.lower())
        print(output)
        output_path = make_path(
            self.directed_result_output_path_template.format(
                method, distance
            )
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

    def test_undirected(self):
        self.check(sampling_method='out_degree', undirected=True)

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
    

class GenCandidateTreeGivenTopicsTest(GenCandidateTreeTest):
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)

        self.some_kws_of_run = {
            'interaction_json_path': make_path('test/data/given_topics/interactions.json'),
            'cand_tree_number': 5,
            'meta_graph_pkl_path_prefix': make_path('test/data/given_topics/meta-graph'),
            'undirected': False,
            'meta_graph_kws': {
                'dist_func': euclidean,
                'decompose_interactions': False,
                'preprune_secs': 8
            },
            'gen_tree_kws': {
                'timespan': 8,
                'U': 0.5,
                'dijkstra': False
            },
            'given_topics': True
        }

        self.meta_pickle_path_common = "decompose_interactions=False--dist_func=euclidean--preprune_secs=8"
        pkl_path = make_path('test/data/given_topics/result--{}.pkl'.format(
            self.meta_pickle_path_common)
        )
        if not os.path.exists(pkl_path):
            print('calc meta graph')
            self._calc_cand_trees_pkl()
        else:
            print('no need to calc meta graph')

    def _calc_cand_trees_pkl(self):
        kws = self.some_kws_of_run.copy()

        run(
            lst,
            calculate_graph=True,
            debug=False,
            print_summary=False,
            result_pkl_path_prefix=make_path('test/data/tmp/test'),
            **kws
        )

    def check(self, test_name, tree_gen_func, **more_args):
        # empty trees are ignored
        # very likely actual tree number should >= 0
        result_pickle_prefix = make_path("test/data/tmp",
                                         "result-{}".format(test_name))
        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=8----%s' %(
            self.meta_pickle_path_common
        )
        kws = self.some_kws_of_run.copy()
        
        if more_args:
            kws.update(more_args)

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
            **kws)

        trees = pkl.load(open(pickle_path))

        assert_true(len(trees) > 0)
        for t in trees:
            assert_true(len(t.edges()) > 0)
        return trees

    # overrides
    def test_variance_method(self):
        self.check('variance', variance_method_euclidean)

    # overrides
    def test_undirected(self):
        pass

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
