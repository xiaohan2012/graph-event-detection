import unittest
import networkx as nx
import random
from nose.tools import assert_equal, assert_true

from .baselines import (grow_tree_general,
                        greedy_choice_by_cost,
                        random_choice,
                        new_frontier)


class Example1():
    @classmethod
    def get_graph(cls):
        g = nx.DiGraph()
        g.add_edges_from([(1, 2, {'c': 1}), (1, 3, {'c': 2}),
                          (1, 4, {'c': 3}), (4, 5, {'c': 4}),
                          (4, 6, {'c': 5}), (3, 7, {'c': 6}),
                          (3, 8, {'c': 7}), (2, 9, {'c': 8}),
                          (2, 10, {'c': 9})])

        for n in g.nodes():
            g.node[n]['r'] = 1
        return g
    
    @classmethod
    def get_data_of_greedy_tree(self):
        U = [6, 16, 30, 100]
        edges = [
            [(1, 2), (1, 3), (1, 4)],
            [(1, 2), (1, 3), (1, 4), (4, 5), (4, 6)],
            [(1, 2), (1, 3), (1, 4), (4, 5), (4, 6), (3, 7), (3, 8)],
            [(1, 2), (1, 3), (1, 4), (4, 5), (4, 6), (3, 7),
             (3, 8), (2, 9), (2, 10)]
        ]
        return U, edges


class Example2():
    @classmethod
    def get_graph(cls):
        g = Example1.get_graph()
        g.add_edges_from([(2, 3, {'c': 1.5}),
                          (1, 6, {'c': 4.5}),
                          (2, 8, {'c': 6.5}),
                          (3, 10, {'c': 8.5})])
        for n in g.nodes():
            g.node[n]['r'] = 1
        return g

    @classmethod
    def get_data_of_greedy_tree(self):
        U = [6, 16, 30, 100]
        edges = [
            [(1, 2), (2, 3), (1, 4)],
            [(1, 2), (2, 3), (1, 4), (4, 5), (1, 6)],
            [(1, 2), (2, 3), (1, 4), (4, 5), (1, 6), (3, 7), (2, 8)],
            [(1, 2), (2, 3), (1, 4), (4, 5), (1, 6), (3, 7), (2, 8),
             (2, 9), (3, 10)]
        ]
        return U, edges


class GrowingTreeTest(unittest.TestCase):
    
    def test_new_frontier(self):
        g = Example1.get_graph()
        g.add_edge(2, 3)  # some modification
        
        nodes = []
        frontier = []
        nodes_to_be_added = [1, 2, 3]

        expected = [
            [(1, 2), (1, 3), (1, 4)],
            [(1, 3), (1, 4), (2, 9), (2, 10), (2, 3)],
            [(1, 4), (2, 9), (2, 10), (3, 7), (3, 8)]
        ]
        for n, edges in zip(nodes_to_be_added, expected):
            frontier = new_frontier(n, nodes, g, frontier)
            nodes.append(n)
            assert_equal(sorted(edges), sorted(frontier))

    def greedy_approach_template(self, data_class):
        g = data_class.get_graph()
        U, expected_edge_list = data_class.get_data_of_greedy_tree()
        
        for u, expected_edges in zip(U, expected_edge_list):
            print(u)
            actual = grow_tree_general(g, 1, u, greedy_choice_by_cost)
            assert_equal(sorted(expected_edges),
                         sorted(actual.edges()))
            for n in actual.nodes():
                assert_true('r' in actual.node[n])
            for u, v in actual.edges():
                assert_true('c' in actual[u][v])

    def test_greedy_grow_tree_1(self):
        self.greedy_approach_template(Example1)

    def test_greedy_grow_tree_2(self):
        self.greedy_approach_template(Example2)

    def test_random_grow_tree_1(self):
        g = Example1.get_graph()
        random.seed(123456)
        U, _ = Example1.get_data_of_greedy_tree()
        expected_edge_list = [
            [(1, 4)],
            [(1, 2), (1, 3), (1, 4), (2, 9)],
            [(1, 2), (1, 3), (1, 4), (3, 8), (4, 5), (4, 6)],
            g.edges()
        ]
        for u, expected_edges in zip(U, expected_edge_list):
            actual = grow_tree_general(g, 1, u, random_choice)
            assert_equal(sorted(expected_edges),
                         sorted(actual.edges()))
