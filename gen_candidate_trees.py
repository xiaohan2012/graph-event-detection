import os
import gensim
import scipy
import cPickle as pickle
import networkx as nx
from datetime import timedelta
import logging

from dag_util import unbinarize_dag, binarize_dag
from lst import lst_dag
from enron_graph import EnronUtil
from meta_graph_stat import MetaGraphStat
from experiment_util import sample_nodes
from util import load_json_by_line
from baselines import greedy_grow, random_grow


logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("cand_tree_genration")
logger.setLevel(logging.INFO)


CURDIR = os.path.dirname(os.path.abspath(__file__))


def run(gen_tree_func,
        timespan=timedelta(weeks=4).total_seconds(),  # 1 month
        enron_json_path=os.path.join(CURDIR, 'data/enron.json'),
        lda_model_path=os.path.join(CURDIR, 'models/model-4-50.lda'),
        corpus_dict_path=os.path.join(CURDIR, 'models/dictionary.pkl'),
        enron_pkl_path=os.path.join(CURDIR, 'data/enron.pkl'),
        cand_tree_number=500,
        result_pkl_path=os.path.join(CURDIR, 'tmp/results.pkl'),
        debug=True,
        calculate_graph=False,
        print_summary=True):
    
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
                                           dist_func=scipy.stats.entropy,
                                           preprune_secs=timespan,
                                           debug=True)

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

    U = 0.5
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

        logger.debug('binarizing dag...')

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

    pickle.dump(results,
                open(result_pkl_path, 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    import random
    import numpy
    random.seed(123456)
    numpy.random.seed(123456)

    import sys
    lst = lambda g, r, U: lst_dag(g, r, U,
                                  edge_weight_decimal_point=2,
                                  debug=False)
    method = sys.argv[1]
    assert method in ('lst', 'greedy', 'random')
    methods = {'lst': lst, 'greedy': greedy_grow, 'random': random_grow}
    print('Running {}'.format(method))

    run(methods[method],
        result_pkl_path='tmp/{}.pkl'.format(method))

