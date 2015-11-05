import string
import ujson as json
from nose.tools import assert_equal
from .meta_graph import convert_to_meta_graph, EnronUtil


def test_meta_graph():
    A, B, C, D, E, F, G = string.ascii_uppercase[:7]
    node_names = range(1, 6)
    sources = [A, A, D, A, G]
    targets = [(B, C, D), (F, ), (E, ), (B, ), (F, )]
    time_stamps = range(1, 6)
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)
    expected_edges = sorted([(1, 2), (1, 3), (2, 4), (1, 4)])
    assert_equal(expected_edges, sorted(graph.edges()))


def test_enron_meta_graph():
    interactions = json.load(open('enron_test.json'))
    graph, _ = EnronUtil.get_meta_graph(interactions)
    assert_equal(sorted([(1, 2), (1, 3), (2, 4), (1, 4)]),
                 sorted(graph.edges()))
    assert_equal(graph.node[1]['body'], 'b1')
    assert_equal(graph.node[1]['subject'], 's1')
    assert_equal(graph.node[2]['body'], '...')
    assert_equal(graph.node[2]['subject'], '...')
    
