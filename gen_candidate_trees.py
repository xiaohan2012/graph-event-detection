import os
import gensim
import cPickle as pickle
import networkx as nx
import ujson as json
import copy
import logging
import itertools

from pprint import pprint
from datetime import timedelta
from scipy.spatial.distance import euclidean, cosine
from scipy.stats import entropy

from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import Manager

from dag_util import unbinarize_dag, binarize_dag, remove_edges_via_dijkstra
from lst import lst_dag, make_variance_cost_func, dp_dag_general
from interactions import InteractionsUtil as IU
from meta_graph_stat import MetaGraphStat
from experiment_util import sample_nodes, \
    sample_nodes_by_out_degree,\
    experiment_signature,\
    get_number_and_percentage
from util import load_json_by_line
from baselines import greedy_grow, random_grow

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


def calc_tree(node_i, r, U,
              gen_tree_func,
              timespan, gen_tree_kws,
              shared_dict,
              print_summary):

    # g is shared in memory
    g = shared_dict['g']
    sub_g = IU.get_rooted_subgraph_within_timespan(
        g, r, timespan, debug=False
    )
    logger.info('nodes procssed {}'.format(node_i))
    logger.debug('getting rooted subgraph within timespan')

    if len(sub_g.edges()) == 0:
        logger.debug("empty rooted sub graph")
        return None

    if gen_tree_kws.get('dijkstra'):
        logger.debug('applying dijkstra')
        sub_g = remove_edges_via_dijkstra(
            sub_g,
            source=r,
            weight=IU.EDGE_COST_KEY
        )

    logger.debug('binarizing dag...')

    binary_sub_g = binarize_dag(sub_g,
                                IU.VERTEX_REWARD_KEY,
                                IU.EDGE_COST_KEY,
                                dummy_node_name_prefix="d_")

    logger.debug('generating tree ')

    tree = gen_tree_func(binary_sub_g, r, U)

    tree = unbinarize_dag(tree,
                          edge_weight_key=IU.EDGE_COST_KEY)

    if len(tree.edges()) == 0:
        logger.debug("empty event tree")
        return None

    if print_summary:
        logger.debug('tree summary:\n{}'.format(get_summary(tree)))

    return tree


def run(gen_tree_func,
        root_sampling_method='uniform',
        undirected=False,
        interaction_json_path=os.path.join(CURDIR, 'data/enron.json'),
        lda_model_path=os.path.join(CURDIR, 'models/model-4-50.lda'),
        corpus_dict_path=os.path.join(CURDIR, 'models/dictionary.pkl'),
        meta_graph_pkl_path_prefix=os.path.join(CURDIR, 'data/enron'),
        cand_tree_number=None,  # higher priority than percentage
        cand_tree_percent=0.1,
        result_pkl_path_prefix=os.path.join(CURDIR, 'tmp/results'),
        meta_graph_kws={
            'dist_func': entropy,
            'decompose_interactions': True,
            'preprune_secs': timedelta(weeks=4)
        },
        gen_tree_kws={
            'timespan': timedelta(weeks=4),
            'U': 0.5,
            'dijkstra': False
        },
        debug=False,
        calculate_graph=False,
        given_topics=False,
        print_summary=False):
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

    meta_graph_pkl_path = "{}--{}.pkl".format(
        meta_graph_pkl_path_prefix,
        experiment_signature(**meta_graph_kws)
    )
    logger.info('meta_graph_pkl_path: {}'.format(meta_graph_pkl_path))

    if calculate_graph:
        logger.info('calculating meta_graph...')
        meta_graph_kws_converted = copy.deepcopy(meta_graph_kws)
        if isinstance(meta_graph_kws_converted['preprune_secs'], timedelta):
            meta_graph_kws_converted['preprune_secs'] = meta_graph_kws['preprune_secs'].total_seconds()
        g = IU.get_topic_meta_graph(
            interactions,
            lda_model=lda_model,
            dictionary=dictionary,
            undirected=undirected,
            debug=True,
            given_topics=given_topics,
            **meta_graph_kws_converted
        )

        logger.info('pickling...')
        nx.write_gpickle(
            IU.compactize_meta_graph(g, map_nodes=False),
            meta_graph_pkl_path
        )

    if not calculate_graph:
        logger.info('loading pickle...')
        g = nx.read_gpickle(meta_graph_pkl_path)
        
    if print_summary:
        logger.debug(get_summary(g))

    cand_tree_number, cand_tree_percent = get_number_and_percentage(
        g.number_of_nodes(),
        cand_tree_number,
        cand_tree_percent
    )

    root_sampling_methods = {
        'uniform': sample_nodes,
        'out_degree': sample_nodes_by_out_degree
    }
    
    logger.info('sampling root nodes...')
    roots = root_sampling_methods[root_sampling_method](g, cand_tree_number)
    logger.info('#roots: {}'.format(len(roots)))
    logger.info('#cand_tree_percent: {}'.format(cand_tree_percent))
    
    shared_dict = {'g': g}
    
    trees = map(lambda (i, r):
                calc_tree(
                    i, r,
                    U=U,
                    gen_tree_func=gen_tree_func,
                    timespan=timespan,
                    gen_tree_kws=gen_tree_kws,
                    shared_dict=shared_dict,
                    print_summary=print_summary),
                itertools.izip(xrange(len(roots)),
                               roots))
    
    trees = filter(None, trees)  # remove Nones

    result_pkl_path = "{}--{}----{}----{}.pkl".format(
        result_pkl_path_prefix,
        experiment_signature(**gen_tree_kws),
        experiment_signature(**meta_graph_kws),
        experiment_signature(
            cand_tree_percent=cand_tree_percent,
            root_sampling=root_sampling_method
        )
    )
    logger.info('result_pkl_path: {}'.format(result_pkl_path))
    pickle.dump(trees,
                open(result_pkl_path, 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)

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

    parser.add_argument('--method', required=True,
                        choices=("lst", "greedy", "random", "variance"),
                        help="Method you will use")
    parser.add_argument('--dist', required=True,
                        choices=('entropy', 'euclidean', 'cosine'),
                        help="Distance function to use")
    parser.add_argument('--root_sampling', required=True,
                        choices=('uniform', 'out_degree'),
                        help="Scheme to sample roots")

    parser.add_argument('--dij', action="store_true",
                        default=False,
                        help="Whether to use Dijkstra or not")
    parser.add_argument('--calc_mg', action="store_true",
                        default=False,
                        help="Whether to recalculate meta graph or not")
    parser.add_argument('--decompose', action="store_true",
                        default=False,
                        help="Whether to decompose interactions")
    parser.add_argument('--undirected', action="store_true",
                        default=False,
                        help="If the interactions are undirected or not")
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

    parser.add_argument('--fixed_point',
                        type=int,
                        default=1,
                        help="How many places to approximate for lst algorithm")

    args = parser.parse_args()

    dist_funcs = {'entropy': entropy, 'euclidean': euclidean, 'cosine': cosine}
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

    methods = {'lst': lst,
               'variance': variance_method,
               'greedy': greedy_grow,
               'random': random_grow}

    # `seconds` of higher priority
    timespan = (args.seconds
                if args.seconds
                else timedelta(weeks=args.weeks))

    pprint(vars(args))

    run(methods[args.method],
        root_sampling_method=args.root_sampling,
        undirected=args.undirected,
        interaction_json_path=args.interaction_path,
        corpus_dict_path=args.corpus_dict_path,
        meta_graph_pkl_path_prefix=args.meta_graph_path_prefix,
        lda_model_path=args.lda_path,
        result_pkl_path_prefix='{}{}'.format(
            args.result_prefix, args.method
        ),
        meta_graph_kws={
            'dist_func': dist_func,
            'decompose_interactions': args.decompose,
            'preprune_secs': timespan,
        },
        gen_tree_kws={
            'timespan': timespan,
            'U': args.U,
            'dijkstra': args.dij
        },
        cand_tree_number=args.cand_n,
        cand_tree_percent=args.cand_n_percent,
        calculate_graph=args.calc_mg,
        given_topics=args.given_topics
    )
