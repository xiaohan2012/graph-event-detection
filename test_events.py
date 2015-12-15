import os
import cPickle as pickle
from nose.tools import assert_equal, assert_true
from events import detect_events, detect_events_given_path

CURDIR = os.path.dirname(os.path.abspath(__file__))


def test_detect_events():
    result_path = os.path.join(CURDIR, 'test/data/cand_trees.pkl')
    cand_trees = pickle.load(open(result_path))
    trees = detect_events(cand_trees, K=5)
    assert_equal(5, len(trees))
    for t1, t2 in zip(trees, trees[1:]):
        assert_true(len(t1.nodes()) >= len(t2.nodes()))


def test_detect_events_given_path():
    result_path = os.path.join(CURDIR, 'test/data/cand_trees.pkl')
    cand_trees = pickle.load(open(result_path))
    expected_trees = detect_events(cand_trees, K=5)
    actual_trees = detect_events_given_path(result_path, K=5)
    for at, et in zip(actual_trees, expected_trees):
        assert_equal(sorted(et.edges()), sorted(at.edges()))
