from .lst import lst_dag
from nose.tools import assert_equal
from networkx.classes.digraph import DiGraph


def test_lst_dag():
    # input
    g = DiGraph()
    g.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])

    g.node[1]['r'] = 1
    g.node[2]['r'] = 1
    g.node[3]['r'] = 1.5
    g.node[4]['r'] = 1

    g[1][2]['c'] = 2
    g[1][3]['c'] = 1
    g[2][4]['c'] = 1
    g[3][4]['c'] = 3

    r = 1  # root
    U = range(6)  # 0...5

    # expected value
    one_node_tree = DiGraph()
    one_node_tree.add_node(1)
    expected_dags = [
        one_node_tree,
        DiGraph([(1, 3)]),
        DiGraph([(1, 3)]),  # DiGraph([(1, 2)])
        DiGraph([(1, 2), (1, 3)]),
        DiGraph([(1, 2), (1, 3), (2, 4)]),
        DiGraph([(1, 2), (1, 3), (2, 4)])
    ]

    for u, expected in zip(U, expected_dags):
        actual = lst_dag(g, r, u)
        print('u={}'.format(u))
        assert_equal(expected.edges(), actual.edges())


# def test_nw_lst_dag():
#     # input
#     g = DiGraph()
#     g.add_edges_from([[1, 2], [1, 3], [2, 4], [3, 4]])
#     g.node[1]['w'] = 1
#     g.node[2]['w'] = 2
#     g.node[3]['w'] = 1
#     g.node[4]['w'] = 1
    
#     r = 1  # root
#     U = range(7)  # 0...6

#     # expected value
#     empty_tree = DiGraph()
#     one_node_tree = DiGraph()
#     one_node_tree.add_node(1)
#     expected_dags = [
#         empty_tree,
#         one_node_tree,
#         DiGraph([(1, 3)]),
#         DiGraph([(1, 3), (3, 4)]),
#         DiGraph([(1, 3), (3, 4)]),  # DiGraph([(1, 2), (2, 3)])
#         DiGraph([(1, 2), (1, 3), (2, 4)]),  # DiGraph([(1, 2), (1, 3), (3, 4)])
#         DiGraph([(1, 2), (1, 3), (2, 4)])  # DiGraph([(1, 2), (1, 3), (3, 4)])
#     ]

#     for u, expected in zip(U, expected_dags):
#         print('u', u)
#         actual = nw_lst_dag(g, r, u)
#         print(actual.edges())
#         assert_equal(actual.edges(), expected.edges())
