from .lst import lst_dag, nw_lst_dag
from nose.tools import assert_equal
from networkx.classes.digraph import DiGraph


def test_lst_dag():
    # input
    dag = DiGraph()
    dag.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])
    dag[1][2]['w'] = 2
    dag[1][3]['w'] = 1
    dag[2][4]['w'] = 1
    dag[3][4]['w'] = 3

    r = 1  # root
    U = range(6)  # 0...5

    # expected value
    one_node_tree = DiGraph()
    one_node_tree.add_node(1)
    expected_dags = [
        one_node_tree,
        DiGraph([(1, 3)]),
        DiGraph([(1, 3)]),  # DiGraph([(1, 2)])
        DiGraph([(1, 2), (2, 4)]),  # DiGraph([(1, 2), (1, 3)])
        DiGraph([(1, 2), (1, 3), (2, 4)]),
        DiGraph([(1, 2), (1, 3), (2, 4)])
    ]

    for u, expected in zip(U, expected_dags):
        actual = lst_dag(dag, r, u)
        print(actual.edges())
        assert_equal(actual.edges(), expected.edges())


def test_nw_lst_dag():
    # input
    dag = DiGraph()
    dag.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])
    dag.node[1]['w'] = 1
    dag.node[2]['w'] = 2
    dag.node[3]['w'] = 1
    dag.node[4]['w'] = 1
    
    r = 1  # root
    U = range(7)  # 0...6

    # expected value
    empty_tree = DiGraph()
    one_node_tree = DiGraph()
    one_node_tree.add_node(1)
    expected_dags = [
        empty_tree,
        one_node_tree,
        DiGraph([(1, 3)]),
        DiGraph([(1, 3), (3, 4)]),
        DiGraph([(1, 3), (3, 4)]),  # DiGraph([(1, 2), (2, 3)])
        DiGraph([(1, 2), (1, 3), (2, 4)]),  # DiGraph([(1, 2), (1, 3), (3, 4)])
        DiGraph([(1, 2), (1, 3), (2, 4)])  # DiGraph([(1, 2), (1, 3), (3, 4)])
    ]

    for u, expected in zip(U, expected_dags):
        print('u', u)
        actual = nw_lst_dag(dag, r, u)
        print(actual.edges())
        assert_equal(actual.edges(), expected.edges())
