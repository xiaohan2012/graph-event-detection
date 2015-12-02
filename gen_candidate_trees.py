import os
import ujson as json
import gensim
import scipy
import cPickle as pickle
import networkx as nx
from datetime import timedelta

from dag_util import unbinarize_dag, binarize_dag
from lst import lst_dag
from enron_graph import EnronUtil
from meta_graph_stat import MetaGraphStat
from experiment_util import sample_nodes

CURDIR = os.path.dirname(os.path.abspath(__file__))

TIMESPAN = timedelta(weeks=4).total_seconds()  # three month

DEBUG = True

CALCULATE_GRAPH = False


def main(enron_json_path='data/enron.json',
         lda_model_path='models/model-4-50.lda',
         corpus_dict_path='models/dictionary.pkl',
         enron_pkl_path='data/enron.pkl',
         cand_tree_number=500,
         result_pkl_path='tmp/results.pkl'):

    input_path = os.path.join(CURDIR, enron_json_path)

    with open(input_path) as f:
        interactions = [json.loads(l) for l in f]
        
    print('loading lda...')
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, lda_model_path)
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, corpus_dict_path)
    )

    if CALCULATE_GRAPH:
        print('calculating meta_graph...')
        g = EnronUtil.get_topic_meta_graph(interactions,
                                           lda_model, dictionary,
                                           dist_func=scipy.stats.entropy,
                                           preprune_secs=TIMESPAN,
                                           debug=True)

        print('pickling...')
        nx.write_gpickle(EnronUtil.compactize_meta_graph(g, map_nodes=False),
                         enron_pkl_path)

    if not CALCULATE_GRAPH:
        print('loading pickle...')
        g = nx.read_gpickle(enron_pkl_path)

    def get_summary(g):
        return MetaGraphStat(
            g, kws={
                'temporal_traffic': {'time_resolution': 'month'},
                'edge_costs': {'max_values': [1.0, 0.1]},
                'topics': False,
                'email_content': False
            }
        ).summary()

    print(get_summary(g))

    roots = sample_nodes(g, cand_tree_number)

    U = 0.5
    results = []

    for ni, r in enumerate(roots):
        if DEBUG:
            print('Nodes procssed {}'.format(ni))
            print('getting rooted subgraph within timespan')

        sub_g = EnronUtil.get_rooted_subgraph_within_timespan(
            g, r, TIMESPAN, debug=False
        )

        if len(sub_g.edges()) == 0:
            print("empty rooted sub graph")
            continue

        if DEBUG:
            print("sub_g summary: \n{}".format(
                get_summary(sub_g)
            ))

        if DEBUG:
            print('binarizing dag...')

        binary_sub_g = binarize_dag(sub_g,
                                    EnronUtil.VERTEX_REWARD_KEY,
                                    EnronUtil.EDGE_COST_KEY,
                                    dummy_node_name_prefix="d_")

        if DEBUG:
            print('lst ing')

        tree = lst_dag(binary_sub_g, r, U,
                       edge_weight_decimal_point=2,
                       debug=False)

        tree = unbinarize_dag(tree, edge_weight_key=EnronUtil.EDGE_COST_KEY)
        if len(tree.edges()) == 0:
            print("empty tree")
            continue

        print('tree summary:\n{}'.format(get_summary(tree)))
        results.append(tree)

    pickle.dump(results,
                open(result_pkl_path, 'w'),
                protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
