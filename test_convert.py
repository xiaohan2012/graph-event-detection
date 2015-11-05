import string
from nose.tools import assert_equal
from .convert_interactions import MetaGraph


def test_convert_enron():
    A, B, C, D, E, F, G = string.ascii_uppercase[:7]
    node_names = range(1, 6)
    sources = [A, A, D, A, G]
    targets = [(B, C, D), (F, ), (E, ), (B, ), (F, )]
    time_stamps = range(1, 6)
    graph = MetaGraph.convert_enron(node_names, sources, targets, time_stamps)
    expected_edges = sorted([(1, 2), (1, 3), (2, 4), (1, 4)])
    assert_equal(expected_edges, sorted(graph.edges()))
