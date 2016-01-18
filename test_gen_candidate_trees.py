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
from .baselines import greedy_grow_by_discounted_reward as greedy_grow, \
    random_grow
from .test_util import remove_tmp_data, make_path
from .experiment_util import experiment_signature


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
    make_variance_cost_func(euclidean,
                            'topics',
                            fixed_point=1,
                            debug=False),
    debug=False
)


class CalcMGMixin(object):
    def update_metagraph_and_produce_if_needed(
            self,
            dist_func=entropy,
            preprune_secs=timedelta(weeks=4),
            U=0.5,
            apply_pagerank=False
    ):
        self.some_kws_of_run = {
            'cand_tree_number': None,
            'cand_tree_percent': 0.1,
            'meta_graph_kws': {
                'dist_func': dist_func,
                'decompose_interactions': False,
                'preprune_secs': preprune_secs,
                'apply_pagerank': apply_pagerank
            },
            'gen_tree_kws': {
                'timespan': preprune_secs,
                'U': U,
                'dijkstra': False
            },
            'root_sampling_method': 'out_degree'
        }

        self.meta_pickle_path_common = experiment_signature(
            decompose_interactions=False,
            dist_func=dist_func,
            preprune_secs=preprune_secs,
            apply_pagerank=apply_pagerank
        )
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


class GenCandidateTreeTest(unittest.TestCase, CalcMGMixin):
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)
        self.update_metagraph_and_produce_if_needed()

    def check(self, test_name, tree_gen_func, undirected=False, **more_args):
        # empty trees are ignored
        # very likely actual tree number should >= 0
        result_pickle_prefix = make_path("test/data/tmp",
                                         "result-{}".format(test_name))
        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=28days----{}----{}'.format(
            self.some_kws_of_run['gen_tree_kws'].get('dijkstra', False),
            self.meta_pickle_path_common,
            experiment_signature(
                cand_tree_percent=self.some_kws_of_run['cand_tree_percent'],
                root_sampling=self.some_kws_of_run['root_sampling_method']
            )
        )
        kws = self.some_kws_of_run.copy()
        
        if undirected:
            kws.update(undirected_params)
        else:
            kws.update(directed_params)
        
        if more_args:
            kws.update(more_args)

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

    def test_greedy_grow_with_pagerank(self):
        self.update_metagraph_and_produce_if_needed(apply_pagerank=True)
        trees = self.check('greedy', greedy_grow)
        for n in trees[0].nodes_iter():
            assert_true(trees[0].node[n]['r'] < 1)

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
        self.result_dir = make_path("test/data/tmp/result-")

        self.directed_params = directed_params
        self.undirected_params = undirected_params

        self.update_result_path_template()

    def update_result_path_template(self,
                                    timespan=timedelta(days=28),
                                    cand_tree_percent=0.01,
                                    sampling_method='uniform',
                                    apply_pagerank=False):
        self.result_output_path_template = "test/data/tmp/result-{}--{}----{}----{}.pkl".format(
            '{}',
            experiment_signature(
                U=0.5,
                dijkstra=False,
                timespan=timespan
            ),
            experiment_signature(
                decompose_interactions=False,
                dist_func='{}',
                preprune_secs=timespan,
                apply_pagerank=apply_pagerank
            ),
            experiment_signature(
                cand_tree_percent=cand_tree_percent,
                root_sampling=sampling_method
            )
        )

    def check(self, method="random", distance="entropy",
              sampling_method="uniform", extra="", undirected=False):
        if undirected:
            more_params = self.undirected_params
        else:
            more_params = self.directed_params

        cmd = """python {} \
        --method={method} \
        --dist={distance_func} \
        --cand_n_percent=0.01 \
        --root_sampling={sampling_method}\
        --result_prefix={result_dir} \
        --weeks=4 --U=0.5 \
        --lda_path={lda_model_path} \
        --interaction_path={interaction_json_path} \
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
        print(output)

        assert_true("traceback" not in output.lower())

        output_path = make_path(
            self.result_output_path_template.format(
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
        self.update_result_path_template(sampling_method='out_degree')
        output = self.check(sampling_method='out_degree')
        assert_true('out_degree' in output)
        
    def test_undirected(self):
        self.update_result_path_template(sampling_method='out_degree')
        self.check(sampling_method='out_degree', undirected=True)

    def test_synthetic(self):
        self.directed_params = {
            'interaction_json_path': make_path(
                'test/data/given_topics/interactions--n_noisy_interactions_fraction=0.1.json'
            ),
            'meta_graph_pkl_path_prefix': make_path('test/data/given_topics/meta-graph'),
            'lda_model_path': None,
            'corpus_dict_path': None,
            'undirected': False
        }
        self.update_result_path_template(timespan=8,
                                         sampling_method='out_degree',
                                         apply_pagerank=True)

        self.check(sampling_method='out_degree', undirected=False,
                   distance='euclidean',
                   extra='--seconds=8 --given_topics --apply_pagerank')

    def test_cand_n(self):
        self.update_result_path_template(cand_tree_percent=0.0972222222222)
        self.check(extra='--cand_n 7')

    def test_apply_pagerank(self):
        self.update_result_path_template(apply_pagerank=True)
        self.check(extra='--apply_pagerank')

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
    

class GenCandidateTreeGivenTopicsTest(GenCandidateTreeTest):
    """sharing some test with GenCandidateTreeTest
    """
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)

        self.some_kws_of_run = {
            'interaction_json_path': make_path(
                'test/data/given_topics/interactions--n_noisy_interactions_fraction=0.1.json'
            ),
            'cand_tree_percent': 0.1,
            'meta_graph_pkl_path_prefix': make_path('test/data/given_topics/meta-graph'),
            'undirected': False,
            'meta_graph_kws': {
                'dist_func': euclidean,
                'decompose_interactions': False,
                'preprune_secs': 8,
                'apply_pagerank': True
            },
            'gen_tree_kws': {
                'timespan': 8,
                'U': 0.5,
                'dijkstra': False
            },
            'given_topics': True
        }

        self.meta_pickle_path_common = experiment_signature(
            decompose_interactions=False,
            dist_func='euclidean',
            preprune_secs=8,
            apply_pagerank=True,
        )
        pkl_path = '{}--{}.pkl'.format(
            self.some_kws_of_run['meta_graph_pkl_path_prefix'],
            self.meta_pickle_path_common
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
        result_pickle_prefix = make_path("test/data/tmp",
                                         "result-{}".format(test_name))

        pickle_path_suffix = 'U=0.5--dijkstra={}--timespan=8----{}----{}'.format(
            self.some_kws_of_run['gen_tree_kws'].get('dijkstra', False),
            self.meta_pickle_path_common,
            experiment_signature(
                cand_tree_percent=self.some_kws_of_run['cand_tree_percent'],
                root_sampling='out_degree',
            )
        )
        kws = self.some_kws_of_run.copy()
        
        if more_args:
            kws.update(more_args)

        pickle_path = "{}--{}.pkl".format(
            result_pickle_prefix,
            pickle_path_suffix
        )

        kws['root_sampling_method'] = 'out_degree'
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
        self.check('variance', variance_method)

    def test_undirected(self):
        # this example is directed,
        # so not applicable
        pass
    
    def test_greedy_grow_with_pagerank(self):
        # as the metagraph path is changed in it
        # so not applicable
        pass

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
