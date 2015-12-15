import string
import scipy
from nose.tools import assert_equal

from .meta_graph import convert_to_meta_graph, convert_to_original_graph
from .enron_graph import EnronUtil

from .test_util import load_meta_graph_necessities


def test_meta_graph():
    A, B, C, D, E, F, G = string.ascii_uppercase[:7]
    interactions = [
        {'sender_id': A, 'recipient_ids': (B, C, D),'datetime': 1, 'message_id': 1},
        {'sender_id': A, 'recipient_ids': [F], 'datetime': 2, 'message_id': 2},
        {'sender_id': D, 'recipient_ids': [E], 'datetime': 3, 'message_id': 3},
        {'sender_id': A, 'recipient_ids': [B], 'datetime': 4, 'message_id': 4},
        {'sender_id': G, 'recipient_ids': [F], 'datetime': 5, 'message_id': 5},
    ]
    EnronUtil.decompose_interactions(interactions)
    node_names, sources, targets, time_stamps = EnronUtil.unzip_interactions(
        EnronUtil.decompose_interactions(interactions)
    )
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)

    expected_edges = sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4')])
    assert_equal(expected_edges, sorted(graph.edges()))


def test_meta_graph_1():
    a, b, c, d = 'a', 'b', 'c', 'd'
    node_names = range(1, 6)
    sources = [a, a, b, d, b]
    targets = [c, b, a, c, d]
    time_stamps = [1, 1, 2, 2, 3]
    
    g = convert_to_meta_graph(node_names, sources, targets, time_stamps)
    
    expected_edges = sorted([(2, 3), (3, 5), (2, 5)])
    assert_equal(expected_edges, sorted(g.edges()))


def test_convert_to_original_graph():
    lda_model, dictionary, interactions = load_meta_graph_necessities()
    g = EnronUtil.get_topic_meta_graph(interactions,
                                       lda_model,
                                       dictionary,
                                       dist_func=scipy.stats.entropy)
    og = convert_to_original_graph(g)
    expected = [('A', 'B'), ('A', 'C'), ('A', 'D'),
                ('A', 'F'), ('D', 'E'), ('D', 'F')]
    assert_equal(sorted(expected), sorted(og.edges()))
