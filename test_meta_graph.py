import string
import scipy
from nose.tools import assert_equal

from .meta_graph import convert_to_meta_graph, \
    convert_to_original_graph, \
    convert_to_meta_graph_undirected
from .interactions import InteractionsUtil as IU, \
    clean_decom_unzip, clean_unzip

from .test_util import load_meta_graph_necessities


def get_example():
    A, B, C, D, E, F, G = string.ascii_uppercase[:7]
    interactions = [
        {'sender_id': A, 'recipient_ids': (B, C, D), 'datetime': 1, 'message_id': 1},
        {'sender_id': A, 'recipient_ids': [F], 'datetime': 2, 'message_id': 2},
        {'sender_id': D, 'recipient_ids': [E], 'datetime': 3, 'message_id': 3},
        {'sender_id': A, 'recipient_ids': [B], 'datetime': 4, 'message_id': 4},
        {'sender_id': G, 'recipient_ids': [F], 'datetime': 5, 'message_id': 5},
    ]
    return interactions


def test_meta_graph_with_prepruning():
    interactions = get_example()
    node_names, sources, targets, time_stamps = clean_unzip(interactions)
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps,
                                  preprune_secs=0)
    assert_equal(0, len(graph.edges()))


def test_meta_graph_with_decomposition():
    interactions = get_example()
    node_names, sources, targets, time_stamps = clean_decom_unzip(
        interactions)
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)

    expected_edges = sorted([('1.B', '2'), ('1.C', '2'), ('1.D', '2'),
                             ('1.B', '4'), ('1.C', '4'), ('1.D', '4'),
                             ('1.D', '3'), ('2', '4')])
    assert_equal(expected_edges, sorted(graph.edges()))


def test_meta_graph_without_decomposition():
    interactions = get_example()
    node_names, sources, targets, time_stamps = clean_unzip(interactions)
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)

    expected_edges = sorted([(1, 2), (1, 4),
                             (1, 3), (2, 4)])
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
    g = IU.get_topic_meta_graph(interactions,
                                lda_model=lda_model,
                                dictionary=dictionary,
                                dist_func=scipy.stats.entropy)
    og = convert_to_original_graph(g)
    expected = [('A', 'B'), ('A', 'C'), ('A', 'D'),
                ('A', 'F'), ('D', 'E'), ('D', 'F')]
    assert_equal(sorted(expected), sorted(og.edges()))


def get_undirected_example():
    node_names = (1, 2, 3, 4)
    participants = [
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'd'),
        ('a', 'c'),
    ]
    time_stamps = (1, 2, 3, 4)
    return node_names, participants, time_stamps


def test_meta_graph_undirected():
    g = convert_to_meta_graph_undirected(
        *get_undirected_example()
    )
    assert_equal(
        set([(1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]),
        set(g.edges())
    )


def test_meta_graph_undirected_with_preprunining():
    g = convert_to_meta_graph_undirected(
        *get_undirected_example(),
        preprune_secs=1
    )
    assert_equal(
        set([(1, 2), (2, 3), (3, 4)]),
        set(g.edges())
    )
