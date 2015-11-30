# Some functiona tests
import os
import ujson as json
import gensim
import scipy
from datetime import timedelta

from .test_lst_dag import _get_more_complicated_example_1
from .dag_util import unbinarize_dag, binarize_dag
from .lst import lst_dag
from .enron_graph import EnronUtil
from .meta_graph_stat import MetaGraphStat

from nose.tools import assert_equal

CURDIR = os.path.dirname(os.path.abspath(__file__))


def test_lst_dag_and_unbinarize_dag():
    """
    lst_dag + unbinarize_dag
    """
    g = _get_more_complicated_example_1()

    U = [0, 2, 3, 4, 100]
    expected_edges_set = [
        [],
        [(1, 7)],
        [(1, 3), (3, 9)],
        [(1, 3), (3, 9), (1, 2)],
        [(1, 2), (1, 3),
         (2, 4), (2, 5), (2, 6),
         (2, 7), (3, 8), (3, 9)]
    ]

    for u, edges in zip(U, expected_edges_set):
        assert_equal(sorted(edges),
                     sorted(
                         unbinarize_dag(
                             lst_dag(g, 1, u),
                             edge_weight_key=EnronUtil.EDGE_COST_KEY
                         ).edges()))


def est_enron_subset():
    input_path = os.path.join(CURDIR, 'test/data/enron-last-100.json')
    with open(input_path) as f:
        interactions = [json.loads(l) for l in f]
        
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, 'test/data/test.lda')
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
    )
    
    g = EnronUtil.get_topic_meta_graph(interactions,
                                       lda_model, dictionary,
                                       dist_func=scipy.stats.entropy)
    U = 20

    g_stat = MetaGraphStat(g)
    print(g_stat.summary())

    timespan = timedelta(weeks=4).total_seconds()  # one month
    for r in g.nodes()[:5]:
        sub_g = EnronUtil.get_rooted_subgraph_within_timespan(g, r, timespan)
        binary_g = binarize_dag(sub_g,
                                EnronUtil.VERTEX_REWARD_KEY,
                                EnronUtil.EDGE_COST_KEY,
                                dummy_node_name_prefix="d_")
        sub_tree = lst_dag(binary_g, r, U,
                           node_reward_key=EnronUtil.VERTEX_REWARD_KEY,
                           edge_cost_key=EnronUtil.EDGE_COST_KEY
                       )
        print(sub_tree)
    
    
