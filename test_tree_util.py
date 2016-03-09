import networkx as nx
from nose.tools import assert_equal

from tree_util import to_bracket_notation, salzburg_ted


def test_to_bracket_notation():
    g = nx.DiGraph()
    g.add_edges_from([
        ('A', 'B'),
        ('B', 'X'),
        ('B', 'Y'),
        ('B', 'F'),
        ('A', 'C'),
    ])
    
    assert_equal(
        '{A{B{F}{X}{Y}}{C}}',
        to_bracket_notation(g)
    )


def test_salzburg_ted():
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
    
    assert_equal(
        1.0,
        salzburg_ted(t1, t2)
    )
