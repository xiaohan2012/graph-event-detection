import random
import os
import unittest
import numpy
import networkx as nx
import cPickle as pkl

from datetime import timedelta
from nose.tools import assert_true, assert_equal, assert_almost_equal
from subprocess import check_output

from gen_candidate_trees import run
from scipy.spatial.distance import cosine

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
    make_variance_cost_func(cosine,
                            'topics',
                            fixed_point=1,
                            debug=False),
    debug=False
)

distance_weights_1 = {'topics': 1.0}
distance_weights_2 = {'topics': 0.2, 'bow': 0.8}
distance_weights_3 = {'topics': 0.5, 'bow': 0.5, 'hashtag_bow': 0.1}


class CalcMGMixin(object):
    def update_metagraph_and_produce_if_needed(
            self,
            dist_func=cosine,
            preprune_secs=timedelta(weeks=4),
            U=2.0,
            apply_pagerank=False,
            distance_weights=distance_weights_2
    ):
        # this is NOT necessary any more
        # the `run` method will calculate the meta graph when needed
        self.some_kws_of_run = {
            'cand_tree_number': None,
            'cand_tree_percent': 0.1,
            'meta_graph_kws': {
                'dist_func': dist_func,
                'preprune_secs': preprune_secs,
                'distance_weights': distance_weights
            },
            'gen_tree_kws': {
                'timespan': preprune_secs,
                'U': U,
                'dijkstra': False
            },
            'root_sampling_method': 'out_degree'
        }

        self.meta_pickle_path_common = experiment_signature(
            dist_func=dist_func,
            preprune_secs=preprune_secs,
            apply_pagerank=apply_pagerank,
            distance_weights=distance_weights
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
        pickle_path_suffix = 'U=2.0--dijkstra={}--timespan=28days----{}----{}'.format(
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

        result_path, mg_path = run(
            tree_gen_func,
            calculate_graph=False,
            print_summary=False,
            result_pkl_path_prefix=result_pickle_prefix,
            **kws)

        trees = pkl.load(open(result_path))

        assert_true(len(trees) > 0)
        for t in trees:
            assert_true(len(t.edges()) > 0)

        return trees, nx.read_gpickle(mg_path)

    def test_if_sender_and_recipient_information_saved(self):
        trees, _ = self.check('lst', lst)
        for t in trees:
            for n in t.nodes():
                assert_true('sender_id' in t.node[n])
                assert_true('recipient_ids' in t.node[n])
        
    def test_greedy_grow(self):
        self.check('greedy', greedy_grow)

    def test_greedy_grow_with_pagerank(self):
        self.update_metagraph_and_produce_if_needed(apply_pagerank=True)
        trees, _ = self.check('greedy', greedy_grow)
        for n in trees[0].nodes_iter():
            assert_true(trees[0].node[n]['r'] < 1)

    def test_random_grow(self):
        self.check('random', random_grow)

    def test_lst_dag(self):
        self.check('lst', lst)

    def test_lst_dag_after_dijkstra(self):
        trees, _ = self.check('lst', lst)

        self.some_kws_of_run['gen_tree_kws']['dijkstra'] = True
        trees_with_dij, _ = self.check('lst', lst)

        for t, t_dij in zip(trees, trees_with_dij):
            assert_true(sorted(t.edges()) != sorted(t_dij))

    def test_variance_method(self):
        self.check('variance', variance_method)

    def test_undirected(self):
        self.check('variance', variance_method,
                   undirected=True)

    def test_distance_weight_using_hashtag_bow(self):
        self.update_metagraph_and_produce_if_needed(
            distance_weights=distance_weights_3
        )
        self.check('greedy', greedy_grow)

    def test_with_roots(self):
        self.some_kws_of_run['roots'] = [54647]
        trees, _ = self.check('lst', lst)
        assert_equal(1, len(trees))
    
    def test_with_recency(self):
        self.some_kws_of_run['meta_graph_kws']['consider_recency'] = True
        self.some_kws_of_run['meta_graph_kws']['tau'] = 0.4
        self.some_kws_of_run['meta_graph_kws']['alpha'] = 0.6
        self.some_kws_of_run['meta_graph_kws']['timestamp_converter'] = lambda s: 2 * s
        self.some_kws_of_run['meta_graph_kws']['distance_weights'] = {'topics': 1.0}
        _, mg = self.check('greey', greedy_grow)
        
        s, t = mg.edges_iter().next()
        time_diff = mg.node[t]['timestamp'] - mg.node[s]['timestamp']
        assert_almost_equal(
            cosine(mg.node[s]['topics'],
                   mg.node[t]['topics'])
            - 0.6 * (0.4 ** (2 * time_diff)),
            mg[s][t]['c']
        )

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
                                    U=2.0,
                                    timespan=timedelta(days=28),
                                    cand_tree_percent=0.01,
                                    sampling_method='uniform',
                                    apply_pagerank=False,
                                    distance_weights=distance_weights_2):
        self.result_output_path_template = "test/data/tmp/result-{}--{}----{}----{}.pkl".format(
            '%s',
            experiment_signature(
                U=U,
                dijkstra=False,
                timespan=timespan
            ),
            experiment_signature(
                dist_func='%s',
                preprune_secs=timespan,
                apply_pagerank=apply_pagerank,
                distance_weights=distance_weights
            ),
            experiment_signature(
                cand_tree_percent=cand_tree_percent,
                root_sampling=sampling_method
            )
        )

    def check(self, method="random", distance="cosine",
              sampling_method="uniform", extra="", undirected=False,
              distance_weights=distance_weights_2):
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
        --weeks=4 --U=2.0 \
        --lda_path={lda_model_path} \
        --interaction_path={interaction_json_path} \
        --corpus_dict_path={corpus_dict_path} \
        --meta_graph_path_prefix={meta_graph_pkl_path_prefix} \
        --weight_for_topics {weight_for_topics} \
        --weight_for_bow {weight_for_bow} \
        --weight_for_hashtag_bow {weight_for_hashtag_bow} \
        {extra}""".format(
            self.script_path,
            method=method,
            distance_func=distance,
            sampling_method=sampling_method,
            result_dir=self.result_dir,
            extra=extra,
            weight_for_topics=distance_weights.get('topics', 0),
            weight_for_bow=distance_weights.get('bow', 0),
            weight_for_hashtag_bow=distance_weights.get('hashtag_bow', 0),
            **more_params
        ).split()
        output = check_output(cmd)
        print(output)

        assert_true("traceback" not in output.lower())

        # output_path = make_path(
        #     self.result_output_path_template % (
        #         method, distance
        #     )
        # )
        # print('output_path:', output_path)
        # assert_true(os.path.exists(output_path))

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

    def test_given_topics(self):
        self.directed_params = {
            'interaction_json_path': make_path(
                'test/data/given_topics/'
                'interactions--n_noisy_interactions_fraction=0.1.json'
            ),
            'meta_graph_pkl_path_prefix': make_path(
                'test/data/given_topics/meta-graph'
            ),
            'lda_model_path': None,
            'corpus_dict_path': None,
            'undirected': False,
        }
        self.update_result_path_template(timespan=8,
                                         sampling_method='out_degree',
                                         apply_pagerank=True,
                                         distance_weights=distance_weights_1
                                     )

        self.check(sampling_method='out_degree', undirected=False,
                   distance='cosine',
                   extra='--seconds=8 --given_topics --apply_pagerank',
                   distance_weights={'topics': 1.0})

    def test_cand_n(self):
        self.update_result_path_template(cand_tree_percent=0.0972222222222)
        self.check(extra='--cand_n 7')

    def test_hashtag_bow(self):
        self.update_result_path_template(distance_weights=distance_weights_3)
        self.check(distance_weights=distance_weights_3)

    def test_apply_pagerank(self):
        self.update_result_path_template(apply_pagerank=True)
        self.check(extra='--apply_pagerank')

    def test_with_event_param_pkl_path(self):
        path = make_path('test/data/tmp/event_param.pkl')
        pkl.dump([{'U': 1.0,
                   'preprune_secs': timedelta(weeks=4),
                   'roots': [54647]}],
                 open(path, 'w'))
        self.update_result_path_template(
            U=1.0,
            timespan=timedelta(weeks=4)
        )
        self.check('greedy',
                   extra='--event_param_pickle_path {}'.format(path)
        )

    def test_with_recency(self):
        self.check('greedy',
                   extra='--recency')
        
    def tearDown(self):
        remove_tmp_data('test/data/tmp')
    

class GenCandidateTreeGivenTopicsTest(GenCandidateTreeTest):
    """sharing some test with GenCandidateTreeTest
    """
    def setUp(self):
        random.seed(1)
        numpy.random.seed(1)

        distance_weights = distance_weights_1  # 'topics' only for given topics
        self.some_kws_of_run = {
            'interaction_json_path': make_path(
                'test/data/given_topics/interactions--n_noisy_interactions_fraction=0.1.json'
            ),
            'cand_tree_percent': 0.1,
            'meta_graph_pkl_path_prefix': make_path('test/data/given_topics/meta-graph'),
            'undirected': False,
            'meta_graph_kws': {
                'dist_func': cosine,
                'preprune_secs': 8,
                'apply_pagerank': True,
                'distance_weights': distance_weights
            },
            'gen_tree_kws': {
                'timespan': 8,
                'U': 2.0,
                'dijkstra': False
            },
            'given_topics': True,
        }

        self.meta_pickle_path_common = experiment_signature(
            dist_func='cosine',
            preprune_secs=8,
            apply_pagerank=True,
            distance_weights=distance_weights
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
            print_summary=False,
            result_pkl_path_prefix=make_path('test/data/tmp/test'),
            **kws
        )

    def check(self, test_name, tree_gen_func, **more_args):
        result_pickle_prefix = make_path("test/data/tmp",
                                         "result-{}".format(test_name))

        pickle_path_suffix = 'U=2.0--dijkstra={}--timespan=8----{}----{}'.format(
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

    def test_distance_weight_using_hashtag_bow(self):
        pass

    def tearDown(self):
        remove_tmp_data('test/data/tmp')
