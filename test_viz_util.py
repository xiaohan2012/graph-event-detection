import networkx as nx
from nose.tools import assert_equal, assert_true, assert_false

from .event_context import extract_event_context
from .viz_util import to_d3_graph, add_subgraph_specific_attributes_to_graph
from .test_event_context import load_example


def test_to_d3_graph():
    g = nx.DiGraph()
    g.add_nodes_from(['a', 'b', 'c'])
    g.add_edges_from([('a', 'b'), ('b', 'c'), ('c', 'a')])
    for n in g.nodes_iter():
        g.node[n]['attr1'] = 'attr1'
        g.node[n]['attr2'] = 'attr2'

    for s, t in g.edges_iter():
        g[s][t]['der1'] = 'der1'
        g[s][t]['der2'] = 'der2'

    d3_g = to_d3_graph(g)
    assert_equal(sorted([{'name': 'a', 'attr1': 'attr1', 'attr2': 'attr2'},
                         {'name': 'b', 'attr1': 'attr1', 'attr2': 'attr2'},
                         {'name': 'c', 'attr1': 'attr1', 'attr2': 'attr2'}
                     ]),
                 sorted(d3_g['nodes'])
    )
    assert_equal(3, len(d3_g['edges']))
    assert_equal(
        sorted([{'source': 0, 'target': 2, 'der1': 'der1', 'der2': 'der2'},
                {'source': 2, 'target': 1, 'der1': 'der1', 'der2': 'der2'},
                {'source': 1, 'target': 0, 'der1': 'der1', 'der2': 'der2'}
            ]),
        sorted(d3_g['edges'])
    )


def test_merge_graphs_adding_special_attributes():
    mother_dag = nx.complete_graph(4)
    new_dag = add_subgraph_specific_attributes_to_graph(
        mother_graph=mother_dag,
        children_graphs_with_attrs=[(nx.complete_graph(2), {'pair': True}),
                                    (nx.complete_graph(3), {'triple': True})]
    )
    for n in new_dag.nodes():
        print(n, new_dag.node[n])
    for s, t in new_dag.edges():
        print(s, t, new_dag[s][t])

    assert_true(new_dag.node[0]['pair'])
    assert_true(new_dag.node[0]['triple'])
    assert_true(new_dag.node[1]['pair'])
    assert_true(new_dag.node[1]['triple'])

    assert_true(new_dag[0][1]['pair'])
    assert_true(new_dag[0][1]['triple'])
    
    assert_true('triple' in new_dag[0][1])
    assert_false('pair' in new_dag[1][2])

    assert_false('pair' in new_dag[3])
    assert_false('triple' in new_dag[3])
