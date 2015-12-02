# Some functiona tests

import unittest
import os
import random
import ujson as json
import gensim
import scipy
from datetime import timedelta

from .test_lst_dag import get_example_3
from .dag_util import unbinarize_dag, binarize_dag
from .lst import lst_dag
from .enron_graph import EnronUtil
from .meta_graph_stat import MetaGraphStat
from .baselines import grow_tree_general, greedy_choice_by_cost, random_choice
from nose.tools import assert_equal

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TreeGenerationMethodsTest(unittest.TestCase):
    def binarize_gen_tree_and_unbinarize(self, r, g, U, expected_edges_set,
                                         gen_tree_func):
        for u, edges in zip(U, expected_edges_set):
            print(u)
            t = gen_tree_func(g, r, u)
            assert_equal(sorted(edges),
                         sorted(
                             unbinarize_dag(
                                 t,
                                 edge_weight_key=EnronUtil.EDGE_COST_KEY
                             ).edges()))

    def test_lst_3(self):
        g, U, _ = get_example_3()
        r = 1
        expected_edges_set = [
            [],
            [(1, 7)],
            [(1, 3), (3, 9)],
            [(1, 3), (3, 9), (1, 2)],
            [(1, 2), (1, 3),
             (2, 4), (2, 5), (2, 6),
             (2, 7), (3, 8), (3, 9)]
        ]
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected_edges_set, lst_dag)

    def test_greedy_3(self):
        g, U, _ = get_example_3()
        r = 1
        expected_edges_set = [
            [],
            [(1, 2), (1, 3)],
            [(1, 2), (1, 3)],
            [(1, 2), (1, 3), (2, 5)],
            [(1, 2), (1, 3),
             (2, 4), (2, 5), (2, 6),
             (1, 7), (3, 8), (3, 9)]
        ]
        greedy_approach = (lambda g, r, U:
                           grow_tree_general(g, r, U, greedy_choice_by_cost))
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected_edges_set,
                                              greedy_approach)

    def test_random_3(self):
        random.seed(123456)
        g, U, _ = get_example_3()
        r = 1
        expected_edges_set = [
            [],
            [(1, 7)],
            [(1, 3), (3, 8)],
            [(1, 2), (1, 3), (2, 7)],
            [(1, 2), (1, 3),
             (2, 4), (2, 5), (2, 6),
             (1, 7), (3, 8), (3, 9)]
        ]
        greedy_approach = (lambda g, r, U:
                           grow_tree_general(g, r, U, random_choice))
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected_edges_set,
                                              greedy_approach)




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
    
    
