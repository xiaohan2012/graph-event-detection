import networkx as nx
from nose.tools import assert_equal, assert_almost_equal

from tree_util import to_bracket_notation, salzburg_ted, \
    tree_similarity_ratio

t1 = nx.DiGraph()
t1.add_edges_from([
    ('A', 'B'),
    ('B', 'X'),
    ('B', 'Y'),
    ('B', 'F'),
    ('A', 'C'),
])
t2 = nx.DiGraph()
t2.add_edges_from([
    ('A', 'B'),
    ('B', 'X'),
    ('B', 'Y'),
    ('B', 'F'),
    ('A', 'D'),
])


def test_to_bracket_notation():
    assert_equal(
        '{A{B{F}{X}{Y}}{C}}',
        to_bracket_notation(t1)
    )


def test_salzburg_ted():
    assert_equal(
        1.0,
        salzburg_ted(t1, t2)
    )


def test_tree_similarity_ratio():
    assert_equal(10. / 12,
                 tree_similarity_ratio(1.0, t1, t2))
