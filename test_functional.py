# Some functiona tests

from .test_lst_dag import _get_more_complicated_example_1
from .dag_util import unbinarize_dag
from .lst import lst_dag
from .enron_graph import EnronUtil

from nose.tools import assert_equal


def test_lst_dag_and_unbinarize_dag():
    """
    lst_dag + unbinarize_dag
    """
    g = _get_more_complicated_example_1()

    print([g.node[n] for n in g.nodes()])
    U = [0, 2, 3, 4, 100]
    expected_edges_set = [
        [],
        [(1, 7)],
        [(1, 3), (3, 9)],
        [(1, 3), (3, 9), (1, 2)],
        [(1, 2), (1, 3),
         (2, 4), (2, 5), (2, 6),
         (2, 7), (3, 8), (3, 9)]
    ]

    for u, edges in zip(U, expected_edges_set):
        assert_equal(sorted(edges),
                     sorted(
                         unbinarize_dag(
                             lst_dag(g, 1, u),
                             edge_weight_key=EnronUtil.EDGE_COST_KEY
                         ).edges()))

