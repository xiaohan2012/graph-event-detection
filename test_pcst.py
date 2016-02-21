import unittest
import networkx as nx
from .pcst import pcst_greedy


class PCSTTest(unittest.TestCase):
    def _run_test(self, g, r, expected_edges, expected_missing_nodes):
        t, x = pcst_greedy(g, r)
        print(t.edges())
        self.assertEqual(sorted(expected_edges),
                         sorted(t.edges()))
        self.assertEqual(sorted(expected_missing_nodes),
                         sorted(x))

    def get_g_with_circle_1(self):
        g = nx.DiGraph()
        g.add_edges_from([('A', 'B', {'c': 2}),
                          ('A', 'C', {'c': 4}),
                          ('C', 'B', {'c': 1}),
                          ('B', 'C', {'c': 2}),
                      ])
        g.node['A']['p'] = 0
        g.node['B']['p'] = 3
        g.node['C']['p'] = 3
        return g

    def test_pcst_digraph(self):
        g = self.get_g_with_circle_1()
        self._run_test(g, 'A',
                      [('A', 'C'), ('C', 'B')],
                      [])

    def test_pcst_digraph_with_isolated_components(self):
        g = self.get_g_with_circle_1()
        g.add_edges_from([('D', 'E', {'c': 0.0})])
        g.node['D']['p'] = 0
        g.node['E']['p'] = 0

        self._run_test(g, 'A',
                      [('A', 'C'), ('C', 'B')],
                      ['D', 'E'])
    
    def get_ivana_example(self):
        A, B, C, D, E = 'A', 'B', 'C', 'D', 'E'
        g = nx.DiGraph()
        g.add_edges_from([
            (A, 3, {'c': 1}),
            (3, B, {'c': 3}),
            (3, C, {'c': 10}),
            (A, 2, {'c': 1}),
            (2, C, {'c': 10}),
            (2, D, {'c': 100}),
            (A, 1, {'c': 10}),
            (1, D, {'c': 100}),
            (A, E, {'c': 10}),
            (A, 5, {'c': 1}),
            (5, E, {'c': 10}),
            (B, 4, {'c': 1}),
            (4, 5, {'c': 10}),
        ])
        nodes = (A, B, C, D, E, 1, 2, 3, 4, 5)
        penalties = (200, 10, 150, 20, 100) + (0., ) * 5
        for n, p in zip(nodes, penalties):
            g.node[n]['p'] = p
        return g

    def test_ivana_example(self):
        # https://homepage.univie.ac.at/ivana.ljubic/research/pcstp/
        g = self.get_ivana_example()
        self._run_test(g, 'A',
                      [('A', 2), ('A', 3), ('A', 'E'), (2, 'C'), (3, 'B')],
                      ['D', 1, 4, 5])

