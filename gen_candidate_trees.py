import os
import gensim
import cPickle as pickle
import networkx as nx
import ujson as json
import copy
import logging

from pprint import pprint
from datetime import timedelta
from scipy.spatial.distance import euclidean, cosine

from dag_util import unbinarize_dag, binarize_dag, remove_edges_via_dijkstra
from lst import lst_dag, make_variance_cost_func, dp_dag_general
from interactions import InteractionsUtil as IU
from meta_graph_stat import MetaGraphStat
from experiment_util import experiment_signature,\
    get_number_and_percentage
from util import load_json_by_line
from baselines import random_grow, greedy_grow_by_discounted_reward
from budget_problem import binary_search_using_charikar
from sampler import RandomSampler, UBSampler, AdaptiveSampler, DeterministicSampler

logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("cand_tree_genration")
logger.setLevel(logging.DEBUG)


CURDIR = os.path.dirname(os.path.abspath(__file__))


def get_summary(g):
    return MetaGraphStat(
        g, kws={
            'temporal_traffic': {'time_resolution': 'month'},
            'edge_costs': {'max_values': [1.0, 0.1]},
            'topics': False,
            'email_content': False
        }
    ).summary()


def calc_tree(node_i, r, dag, U,
              gen_tree_func,
              gen_tree_kws,
              print_summary,
              should_binarize_dag=False):
    # g is shared in memory

    logger.info('nodes procssed {}'.format(node_i))
    if len(dag.edges()) == 0:
        logger.debug("empty rooted sub graph")
        return None

    if gen_tree_kws.get('dijkstra'):
        logger.debug('applying dijkstra')
        dag = remove_edges_via_dijkstra(
            dag,
            source=r,
            weight=IU.EDGE_COST_KEY
        )

    if should_binarize_dag:
        logger.debug('binarizing dag...')

        dag = binarize_dag(dag,
                           IU.VERTEX_REWARD_KEY,
                           IU.EDGE_COST_KEY,
                           dummy_node_name_prefix="d_")

    logger.debug('generating tree ')

    tree = gen_tree_func(dag, r, U)

    if should_binarize_dag:
        tree = unbinarize_dag(tree,
                              edge_weight_key=IU.EDGE_COST_KEY)
    if len(tree.edges()) == 0:
        logger.debug("empty event tree")
        return None

    if print_summary:
        logger.debug('tree summary:\n{}'.format(get_summary(tree)))

    return tree


def run(gen_tree_func,
        root_sampling_method='random',
        interaction_json_path=os.path.join(CURDIR, 'data/enron.json'),
        lda_model_path=os.path.join(CURDIR, 'models/model-4-50.lda'),
        corpus_dict_path=os.path.join(CURDIR, 'models/dictionary.pkl'),
        meta_graph_pkl_path_prefix=os.path.join(CURDIR, 'data/enron'),
        cand_tree_number=None,  # higher priority than percentage
        cand_tree_percent=0.1,
        result_pkl_path_prefix=os.path.join(CURDIR, 'tmp/results'),
        result_suffix='',
        all_paths_pkl_prefix='',
        all_paths_pkl_suffix='',
        true_events_path='',
        meta_graph_kws={
            'dist_func': cosine,
            'preprune_secs': timedelta(weeks=4),
            'distance_weights': {'topics': 0.2,
                                 'bow': 0.8},
            'consider_recency': False,
            'tau': 0.8,
            'alpha': 0.5,
            'timestamp_converter': lambda s: s
        },
        gen_tree_kws={
            'timespan': timedelta(weeks=4),
            'U': 0.5,
            'dijkstra': False
        },
        convert_time=True,
        roots=None,
        calculate_graph=False,
        given_topics=False,
        print_summary=False,
        should_binarize_dag=False):
    if isinstance(gen_tree_kws['timespan'], timedelta):
        timespan = gen_tree_kws['timespan'].total_seconds()
    else:
        timespan = gen_tree_kws['timespan']
    U = gen_tree_kws['U']
        
    try:
        interactions = json.load(open(interaction_json_path))
    except ValueError:
        interactions = load_json_by_line(interaction_json_path)

    logger.info('loading lda from {}'.format(lda_model_path))
    if not given_topics:
        lda_model = gensim.models.ldamodel.LdaModel.load(
            os.path.join(CURDIR, lda_model_path)
        )
        dictionary = gensim.corpora.dictionary.Dictionary.load(
            os.path.join(CURDIR, corpus_dict_path)
        )
    else:
        lda_model = None
        dictionary = None

    # if not meta_graph_kws['consider_recency']:
    #     del meta_graph_kws['tau']
    #     del meta_graph_kws['alpha']

    meta_graph_pkl_path = "{}--{}.pkl".format(
        meta_graph_pkl_path_prefix,
        experiment_signature(**meta_graph_kws)
    )
    logger.info('meta_graph_pkl_path: {}'.format(meta_graph_pkl_path))

    if calculate_graph or not os.path.exists(meta_graph_pkl_path):
        # we want to calculate the graph or
        # it's not there so we have to
        logger.info('calculating meta_graph...')
        meta_graph_kws_copied = copy.deepcopy(meta_graph_kws)

        if isinstance(meta_graph_kws_copied['preprune_secs'], timedelta):
            meta_graph_kws_copied['preprune_secs'] = meta_graph_kws['preprune_secs'].total_seconds()
        g = IU.get_topic_meta_graph(
            interactions,
            lda_model=lda_model,
            dictionary=dictionary,
            undirected=False,  # deprecated
            given_topics=given_topics,
            decompose_interactions=False,
            convert_time=convert_time,
            **meta_graph_kws_copied
        )

        logger.info('pickling...')
        nx.write_gpickle(
            IU.compactize_meta_graph(g, map_nodes=False),
            meta_graph_pkl_path
        )
    else:
        logger.info('loading pickle...')
        g = nx.read_gpickle(meta_graph_pkl_path)
        
    if print_summary:
        logger.debug(get_summary(g))

    assert g.number_of_nodes() > 0, 'empty graph!'

    if not roots:
        cand_tree_number, cand_tree_percent = get_number_and_percentage(
            g.number_of_nodes(),
            cand_tree_number,
            cand_tree_percent
        )
        if root_sampling_method == 'random':
            root_sampler = RandomSampler(g, timespan)
        elif root_sampling_method == 'upperbound':
            root_sampler = UBSampler(g, U, timespan)
        else:
            root_sampler = AdaptiveSampler(g, U, timespan)
    else:
        logger.info('Roots given')
        cand_tree_number = len(roots)
        root_sampler = DeterministicSampler(g, roots, timespan)
    
    logger.info('#roots: {}'.format(cand_tree_number))
    logger.info('#cand_tree_percent: {}'.format(
        cand_tree_number / float(g.number_of_nodes()))
    )

    trees = []
    dags = []
    for i in xrange(cand_tree_number):
        root, dag = root_sampler.take()
        dags.append(dag)

        tree = calc_tree(i, root, dag, U,
                         gen_tree_func,
                         gen_tree_kws,
                         print_summary,
                         should_binarize_dag=should_binarize_dag)
        trees.append(tree)
        
        root_sampler.update(root, tree)

    def make_detailed_path(prefix, suffix):
        return "{}--{}----{}----{}{}.pkl".format(
            prefix,
            experiment_signature(**gen_tree_kws),
            experiment_signature(**meta_graph_kws),
            experiment_signature(
                cand_tree_percent=cand_tree_percent,
                root_sampling=root_sampling_method
            ),
            suffix
        )
    result_pkl_path = make_detailed_path(result_pkl_path_prefix,
                                         result_suffix)

    logger.info('result_pkl_path: {}'.format(result_pkl_path))
    pickle.dump(trees,
                open(result_pkl_path, 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(dags,
                open(result_pkl_path+'.dag', 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)
    
    logger.info('Dumping the paths info')
    all_paths_pkl_path = make_detailed_path(all_paths_pkl_prefix,
                                            all_paths_pkl_suffix)
    paths_dict = {'interactions': interaction_json_path,
                  'meta_graph': meta_graph_pkl_path,
                  'result': result_pkl_path,
                  'true_events': true_events_path,
                  'self': all_paths_pkl_path
    }
    pickle.dump(
        paths_dict,
        open(all_paths_pkl_path, 'w')
    )
    return paths_dict

if __name__ == '__main__':
    import random
    import numpy
    random.seed(123456)
    numpy.random.seed(123456)

    import argparse
    parser = argparse.ArgumentParser(
        description="Generate candidate event trees"
    )
    parser.add_argument('--interaction_path', required=True,
                        type=str,
                        help="Path to the interaction json file")
    parser.add_argument('--lda_path', required=True,
                        help="Path of LDA model")
    parser.add_argument('--corpus_dict_path', required=True,
                        help="Path of corpus dictionary")
    parser.add_argument('--meta_graph_path_prefix', required=True,
                        help="Prefix of path of meta graph pickle")
    parser.add_argument('--calc_mg', action='store_true',
                        help="calc meta graph or not")

    parser.add_argument('--method', required=True,
                        choices=("lst", "greedy",
                                 "random", "quota"),
                        help="Method you will use")
    parser.add_argument('--dist', required=True,
                        choices=('euclidean', 'cosine'),
                        help="Distance function to use")
    parser.add_argument('--root_sampling', default='random',
                        choices=('random', 'upperbound', 'adaptive'),
                        help="Scheme to sample roots")

    parser.add_argument('--dij', action="store_true",
                        default=False,
                        help="Whether to use Dijkstra or not")
    parser.add_argument('--cand_n',
                        default=None,
                        type=int,
                        help="Number of candidate trees to generate")
    parser.add_argument('--cand_n_percent',
                        type=float,
                        default=0.1,
                        help="Percentage of candidate trees to generate in terms of total number of nodes")

    parser.add_argument('--result_prefix',
                        default='tmp/result-',
                        help="Prefix of result path")
    parser.add_argument('--result_suffix',
                        default='',
                        help="Suffix of result path")
    parser.add_argument('--all_paths_pkl_prefix',
                        required=True)
    parser.add_argument('--all_paths_pkl_suffix',
                        default='')
    parser.add_argument('--true_events_path',
                        default='')
                
    parser.add_argument('--weeks',
                        type=int,
                        default=4,
                        help="Time span in terms of weeks")
    parser.add_argument('--seconds',
                        type=int,
                        default=0,
                        help="Time span in terms of seconds")
    parser.add_argument('--given_topics',
                        action='store_true',
                        help="whether topics are given")

    parser.add_argument('--U',
                        type=float,
                        default=0.5,
                        help="Parameter U")
    parser.add_argument('--event_param_pickle_path',
                        default=None,
                        help="Path of pickle file that contains the U, preprune_secs and roots parameters")

    parser.add_argument('--fixed_point',
                        type=int,
                        default=1,
                        help="How many places to approximate for lst algorithm")
    parser.add_argument('--weight_for_topics',
                        type=float,
                        default=0.2)
    parser.add_argument('--weight_for_bow',
                        type=float,
                        default=0.8)
    parser.add_argument('--weight_for_hashtag_bow',
                        type=float,
                        default=0.0)

    parser.add_argument('--recency',
                        action='store_true',
                        default=False,
                        help="whether considering recency or not")
    parser.add_argument('--tau', type=float,
                        default=0.8,
                        help="the \tau value in the recency function"
    )
    parser.add_argument('--alpha', type=float,
                        default=0.5,
                        help="the \alpha value in the recency function"
    )
    parser.add_argument('--time_diff_unit', type=str,
                        default='day',
                        choices=('sec', 'day'),
                        help="How do we consider *one* recency, 1 second or 1 day?"
    )

    parser.add_argument('--not_convert_time',
                        action='store_true',
                        help="whether convert datetime or not(for synthetic data experiment)")

    parser.add_argument('--charikar_level',
                        type=int,
                        default=2,
                        help="the `level` parameter in charikar's algorithm"
    )

    args = parser.parse_args()

    dist_funcs = {'euclidean': euclidean, 'cosine': cosine}
    dist_func = dist_funcs[args.dist]

    lst = lambda g, r, U: lst_dag(g, r, U,
                                  edge_weight_decimal_point=args.fixed_point,
                                  debug=False)
    variance_method = lambda g, r, U: dp_dag_general(
        g, r,
        int(U*(10**args.fixed_point)),
        make_variance_cost_func(dist_func, 'topics',
                                args.fixed_point),
        debug=False
    )

    quota_based_method = lambda g, r, U: binary_search_using_charikar(
        g, r, U, args.charikar_level
    )

    methods = {'lst': lst,
               'variance': variance_method,
               'greedy': greedy_grow_by_discounted_reward,
               'quota': quota_based_method,
               'random': random_grow
    }
    if args.method == 'lst':
        should_binarize_dag = True
    else:
        should_binarize_dag = False

    pprint(vars(args))

    distance_weights = {}
    if args.weight_for_topics > 0:
        distance_weights['topics'] = args.weight_for_topics
    if args.weight_for_bow > 0:
        distance_weights['bow'] = args.weight_for_bow
    if args.weight_for_hashtag_bow > 0:
        distance_weights['hashtag_bow'] = args.weight_for_hashtag_bow

    if args.event_param_pickle_path:
        params = pickle.load(open(args.event_param_pickle_path))[0]  # take the first one
        timespan = params['preprune_secs']
        U = params['U']
        roots = params['roots']
    else:
        # `seconds` of higher priority
        timespan = (args.seconds
                    if args.seconds
                    else timedelta(weeks=args.weeks))
        U = args.U
        roots = None

    if args.time_diff_unit:
        time_unit2converter = {'sec': lambda s: s,
                               'day': lambda s: s / 86400.}
        timestamp_converter = time_unit2converter[args.time_diff_unit]
        
    paths = run(methods[args.method],
                root_sampling_method=args.root_sampling,
                interaction_json_path=args.interaction_path,
                corpus_dict_path=args.corpus_dict_path,
                meta_graph_pkl_path_prefix=args.meta_graph_path_prefix,
                lda_model_path=args.lda_path,
                result_pkl_path_prefix='{}{}'.format(
                    args.result_prefix, args.method
                ),
                result_suffix=args.result_suffix,
                all_paths_pkl_prefix=args.all_paths_pkl_prefix,
                all_paths_pkl_suffix=args.all_paths_pkl_suffix,
                true_events_path=args.true_events_path,
                meta_graph_kws={
                    'dist_func': dist_func,
                    'preprune_secs': timespan,
                    'distance_weights': distance_weights,
                    'consider_recency': args.recency,
                    'tau': args.tau,
                    'alpha': args.alpha,
                    'timestamp_converter': timestamp_converter
                },
                gen_tree_kws={
                    'timespan': timespan,
                    'U': U,
                    'dijkstra': args.dij
                },
                cand_tree_number=args.cand_n,
                cand_tree_percent=args.cand_n_percent,
                calculate_graph=args.calc_mg,
                given_topics=args.given_topics,
                roots=roots,
                convert_time=not args.not_convert_time,
                should_binarize_dag=should_binarize_dag
            )

    import cPickle as pkl
    pkl.dump(paths, open('.paths.pkl', 'w'))
