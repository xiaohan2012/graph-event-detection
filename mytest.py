import os
import ujson as json
import gensim
import scipy
import cPickle  as pickle
import numpy as np
from datetime import timedelta

from dag_util import unbinarize_dag, binarize_dag, assert_no_cycle
from lst import lst_dag
from enron_graph import EnronUtil
from meta_graph_stat import MetaGraphStat
from experiment_util import sample_nodes

CURDIR = os.path.dirname(os.path.abspath(__file__))

input_path = os.path.join(CURDIR, 'data/enron.json')
with open(input_path) as f:
    interactions = [json.loads(l) for l in f]

print('loading lda...')
lda_model = gensim.models.ldamodel.LdaModel.load(
    os.path.join(CURDIR, 'test/data/test.lda')
)
dictionary = gensim.corpora.dictionary.Dictionary.load(
    os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
)

print('calculating meta_graph...')
g = EnronUtil.get_topic_meta_graph(interactions,
                                   lda_model, dictionary,
                                   dist_func=scipy.stats.entropy,
                                   debug=True)


# pickle.dump(g, open('test/data/enron-last-100-meta.pkl', 'w'))
print('pickling...')
pickle.dump(g, open('data/enron.pkl', 'w'))
# g = pickle.load(open('test/data/enron-last-100-meta.pkl', 'r'))

assert_no_cycle(g)

print(MetaGraphStat(g).summary())

timespan = timedelta(weeks=48).total_seconds()  # one month

# roots = [u'233107.206',  # (30, datetime.datetime(2001, 2, 3, 12, 19))
#          u'253127.1180']

roots = sample_nodes(g, 50)

U = 0.5
results = []

debug = False
for r in roots:
    if debug:
        print('getting rooted subgraph within timespan')
    
    sub_g = EnronUtil.get_rooted_subgraph_within_timespan(
        g, r, timespan, debug=False
    )

    if len(sub_g.edges()) == 0:
        print("empty rooted sub graph")
        continue

    if debug:
        print("sub_g summary: \n{}".format(
            MetaGraphStat(sub_g).summary())
          )

    print('binarizing dag')
    binary_sub_g = binarize_dag(sub_g,
                                EnronUtil.VERTEX_REWARD_KEY,
                                EnronUtil.EDGE_COST_KEY,
                                dummy_node_name_prefix="d_")
    assert_no_cycle(binary_sub_g)
    if debug:
        print("binary_sub_g summary: \n{}".format(
            MetaGraphStat(binary_sub_g).summary())
          )
    print('lst ing')
    tree = lst_dag(binary_sub_g, r, U,
                   edge_weight_decimal_point=2,
                   debug=False)

    print('tree summary:\n{}'.format(MetaGraphStat(tree).summary()))
    results.append(unbinarize_dag(tree))

pickle.dump(results, open('tmp/results.json', 'w'))


# def sample_nodes_by_partial_importance(g, nodes_sample_size=100,
#                  sample_pool_size=1000):
#     nodes_pool = sorted(g.nodes(),
#                         key=lambda n: g.out_degree(n),
#                         reverse=True)[:sample_pool_size]
#     return nodes_pool[np.random.permutation(len(nodes_pool))[:nodes_sample_size]]        
