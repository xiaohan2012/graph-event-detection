import os
import gensim
import cPickle as pickle
import networkx as nx
from datetime import timedelta
import logging

from dag_util import unbinarize_dag, binarize_dag, remove_edges_via_dijkstra
from lst import lst_dag
from enron_graph import EnronUtil
from meta_graph_stat import MetaGraphStat
from experiment_util import sample_nodes, experiment_signature
from util import load_json_by_line
from baselines import greedy_grow, random_grow
from scipy.spatial.distance import euclidean, cosine
from scipy.stats import entropy

logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("cand_tree_genration")
logger.setLevel(logging.DEBUG)


CURDIR = os.path.dirname(os.path.abspath(__file__))


def run(gen_tree_func,
        enron_json_path=os.path.join(CURDIR, 'data/enron.json'),
        lda_model_path=os.path.join(CURDIR, 'models/model-4-50.lda'),
        corpus_dict_path=os.path.join(CURDIR, 'models/dictionary.pkl'),
        enron_pkl_path_prefix=os.path.join(CURDIR, 'data/enron'),
        cand_tree_number=500,
        result_pkl_path_prefix=os.path.join(CURDIR, 'tmp/results'),
        meta_graph_kws={
            'dist_func': entropy,
            'decompose_interactions': True,
        },
        gen_tree_kws={
            'timespan': timedelta(weeks=4),
            'U': 0.5,
            'dijkstra': False
        },
        debug=False,
        calculate_graph=False,
        print_summary=False):
    result_pkl_path = "{}--{}----{}.pkl".format(
        result_pkl_path_prefix,
        experiment_signature(**gen_tree_kws),
        experiment_signature(**meta_graph_kws)
    )
    timespan = gen_tree_kws['timespan'].total_seconds()
    U = gen_tree_kws['U']
    
    enron_pkl_path = "{}--{}.pkl".format(
        enron_pkl_path_prefix,
        experiment_signature(**meta_graph_kws)
    )
    print('enron_pkl_path:', enron_pkl_path)
    
    people_data_path = os.path.join(CURDIR, 'data/people.json')

    interactions = load_json_by_line(enron_json_path)
    people_info = load_json_by_line(people_data_path)
        
    logger.info('loading lda...')
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, lda_model_path)
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, corpus_dict_path)
    )

    if calculate_graph:
        logger.info('calculating meta_graph...')
        g = EnronUtil.get_topic_meta_graph(interactions,
                                           lda_model, dictionary,
                                           preprune_secs=timespan,
                                           debug=True,
                                           **meta_graph_kws)

        logger.info('pickling...')
        nx.write_gpickle(EnronUtil.compactize_meta_graph(g, map_nodes=False),
                         enron_pkl_path)

    if not calculate_graph:
        logger.info('loading pickle...')
        g = nx.read_gpickle(enron_pkl_path)
        
    def get_summary(g):
        return MetaGraphStat(
            g, kws={
                'temporal_traffic': {'time_resolution': 'month'},
                'edge_costs': {'max_values': [1.0, 0.1]},
                'topics': False,
                'email_content': False,
                'participants': {
                    'people_info': people_info,
                    'interactions': interactions,
                    'top_k': 5
                }
            }
        ).summary()

    if print_summary:
        logger.debug(get_summary(g))

    roots = sample_nodes(g, cand_tree_number)

    results = []

    for ni, r in enumerate(roots):
        logger.info('Nodes procssed {}'.format(ni))
        logger.debug('Getting rooted subgraph within timespan')

        sub_g = EnronUtil.get_rooted_subgraph_within_timespan(
            g, r, timespan, debug=False
        )

        if len(sub_g.edges()) == 0:
            logger.debug("empty rooted sub graph")
            continue

        if gen_tree_kws.get('dijkstra'):
            logger.debug('applying dijkstra')
            sub_g = remove_edges_via_dijkstra(
                sub_g,
                source=r,
                weight=EnronUtil.EDGE_COST_KEY
            )

        logger.debug('binarizing dag...')

        def check_g_attrs(g):
            logger.debug("checking sender id")
            for n in g.nodes():
                if isinstance(n, basestring) and not n.startswith('dummy'):
                    assert 'sender_id' in g.node[n]
        check_g_attrs(sub_g)

        binary_sub_g = binarize_dag(sub_g,
                                    EnronUtil.VERTEX_REWARD_KEY,
                                    EnronUtil.EDGE_COST_KEY,
                                    dummy_node_name_prefix="d_")
        
        logger.debug('generating tree ')

        tree = gen_tree_func(binary_sub_g, r, U)

        tree = unbinarize_dag(tree, edge_weight_key=EnronUtil.EDGE_COST_KEY)
        if len(tree.edges()) == 0:
            logger.debug("empty tree")
            continue

        if print_summary:
            logger.debug('tree summary:\n{}'.format(get_summary(tree)))

        results.append(tree)

    print('result_pkl_path:', result_pkl_path)
    pickle.dump(results,
                open(result_pkl_path, 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    import random
    import numpy
    random.seed(123456)
    numpy.random.seed(123456)

    lst = lambda g, r, U: lst_dag(g, r, U,
                                  edge_weight_decimal_point=2,
                                  debug=False)
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate candidate event trees"
    )
    parser.add_argument('--method', required=True,
                        choices=("lst", "greedy", "random"),
                        help="Method you will use")
    parser.add_argument('--dist', required=True,
                        choices=('entropy', 'euclidean', 'cosine'),
                        help="Distance function to use")
    parser.add_argument('--dij', action="store_true",
                        default=False,
                        help="Whether to use Dijkstra or not")
    parser.add_argument('--calc_mg', action="store_true",
                        default=False,
                        help="Whether to recalculate meta graph or not")
    parser.add_argument('--decompose', action="store_true",
                        default=False,
                        help="Whether to decompose interactions")
    parser.add_argument('--cand_n',
                        default=500,
                        type=int,
                        help="Number of candidate trees to generate")
    parser.add_argument('--res_dir',
                        default='tmp',
                        help="directory to save the results")

    parser.add_argument('--lda',
                        help="Path of LDA model")

    parser.add_argument('--weeks',
                        type=int,
                        default=4,
                        help="Time span in terms of weeks")

    parser.add_argument('--U',
                        type=float,
                        default=0.5,
                        help="Parameter U")

    args = parser.parse_args()

    methods = {'lst': lst, 'greedy': greedy_grow, 'random': random_grow}
    dist_funcs = {'entropy': entropy, 'euclidean': euclidean, 'cosine': cosine}

    dist_func = dist_funcs[args.dist]
    
    print('Running: {}'.format(args.method))
    print('Dist func: {}'.format(args.dist))
    print('Decompose interactions: {}'.format(args.decompose))
    print('Dijkstra: {}'.format(args.dij))

    run(methods[args.method],
        result_pkl_path_prefix='{}/result-{}'.format(
            args.res_dir, args.method),
        meta_graph_kws={
            'dist_func': dist_func,
            'decompose_interactions': args.decompose
        },
        gen_tree_kws={
            'timespan': timedelta(weeks=args.weeks),
            'U': args.U,
            'dijkstra': args.dij
        },
        cand_tree_number=args.cand_n,
        calculate_graph=args.calc_mg
    )
