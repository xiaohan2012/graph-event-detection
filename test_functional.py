# Some functiona tests

import unittest
import os
import random
import ujson as json
import gensim
import scipy
from datetime import timedelta

from .test_lst_dag import (get_example_3, get_example_4,
                           get_example_4_float, get_example_5,
                           get_example_6)
from .dag_util import unbinarize_dag, binarize_dag, remove_edges_via_dijkstra
from .lst import lst_dag
from .interactions import InteractionsUtil
from .meta_graph_stat import MetaGraphStat
from .baselines import greedy_grow, random_grow
from nose.tools import assert_equal

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TreeGenerationMethodsTest(unittest.TestCase):
    def binarize_gen_tree_and_unbinarize(self, r, g, U, expected_edges_set,
                                         gen_tree_func,
                                         **gen_tree_kws):
        g = binarize_dag(g,
                         InteractionsUtil.VERTEX_REWARD_KEY,
                         InteractionsUtil.EDGE_COST_KEY)
        for u, edges in zip(U, expected_edges_set):
            print(u)
            t = gen_tree_func(g, r, u, **gen_tree_kws)
            assert_equal(sorted(edges),
                         sorted(
                             unbinarize_dag(
                                 t,
                                 edge_weight_key=InteractionsUtil.EDGE_COST_KEY
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

    def test_lst_4(self):
        g, U, expected = get_example_4()
        r = 0
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected,
                                              lst_dag)

    def test_lst_5(self):
        g, U, expected = get_example_5()
        r = 0
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected,
                                              lst_dag)

    def test_lst_6(self):
        # sub optimal
        g, U, expected = get_example_6()
        r = 0
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected,
                                              lst_dag)

    def test_lst_6_after_dijkstra(self):
        # now, should be optimal
        g, U, _ = get_example_6()
        expected = [[(0, 1), (1, 3), (0, 2), (2, 4), (2, 5)]]
        r = 0
        t = remove_edges_via_dijkstra(g, r)
        self.binarize_gen_tree_and_unbinarize(r, t, U,
                                              expected,
                                              lst_dag)

    def test_lst_4_float(self):
        g, U, expected = get_example_4_float()
        r = 0
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected,
                                              lst_dag,
                                              edge_weight_decimal_point=6,
                                              debug=True)

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

        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected_edges_set,
                                              greedy_grow)

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
        self.binarize_gen_tree_and_unbinarize(r, g, U,
                                              expected_edges_set,
                                              random_grow)
