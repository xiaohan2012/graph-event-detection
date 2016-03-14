import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import networkx as nx
from subprocess import check_output

from dag_util import get_roots
from test_util import make_path


def to_bracket_notation(tree):
    def aux(node):
        nbrs = sorted(tree.neighbors(node))
        if len(nbrs) == 0:
            return '{%s}' % node
        else:
            return '{%s%s}' % (
                node,
                ''.join([aux(n) for n in nbrs])
            )
    if tree.number_of_nodes() == 0:
        return '{}'
    else:
        assert nx.is_arborescence(tree)
        return aux(get_roots(tree)[0])
    

JAR_PATH = make_path('external/APTED-0.1.1.jar')


def salzburg_ted(tree1, tree2):
    """
    tree edit distance

    From [Source](tree-edit-distance.dbresearch.uni-salzburg.at/#download)
    """
    print('##### 1 ######')
    print(to_bracket_notation(tree1))
    print('##### 2 ######')
    print(to_bracket_notation(tree2))
    output = check_output('java -jar {} --trees {} {}'.format(
        JAR_PATH,
        to_bracket_notation(tree1),
        to_bracket_notation(tree2)
    ).split())
    
    try:
        return float(output)
    except ValueError:
        print(output)
        raise


def tree_similarity_ratio(ted, t1, t2):
    """
    Return the similarity ratio from 0 to 1 between two trees given their edit distance
    
    `ratio` idea from [DiffLib](https://fossies.org/dox/Python-3.5.1/difflib_8py_source.html)
    """
    print(ted)
    import networkx as nx
    empty_tree = nx.DiGraph()
    print('#nodes',
          t1.number_of_nodes(),
          t2.number_of_nodes())
    print('ted against empty_tree',
          salzburg_ted(t1, empty_tree),
          salzburg_ted(t2, empty_tree))

    return 1 - 2 * ted/(t1.number_of_nodes() + t2.number_of_nodes())
    

def tree_density(tree, X, edge_weight='c'):
    cost = sum(tree[s][t][edge_weight]
               for s, t in tree.edges_iter())
    try:
        return float(cost) / len(set(tree.nodes()).intersection(X))
    except ZeroDivisionError:
        return float('inf')


def draw_pred_tree_against_true_tree(pred_tree, true_tree, meta_graph,
                                     draw_which='together',
                                     output_path_suffix=''):
    """

    Draw predicted event against the true event
    while using the meta graph as the background

    doesn't draw the entire meta_graph, just nx.compose(pred_tree, true_tree)
    """
    # some checking
    for n in true_tree.nodes_iter():
        assert meta_graph.has_node(n), n
    for s, t in true_tree.edges_iter():
        assert meta_graph.has_edge(s, t), (s, t,
                                           (meta_graph.node[s]['sender_id'], meta_graph.node[s]['recipient_ids']),
                                           (meta_graph.node[t]['sender_id'], meta_graph.node[t]['recipient_ids']),
                                           meta_graph.node[s]['timestamp'],
                                           meta_graph.node[t]['timestamp'],
                                           meta_graph.node[t]['timestamp'] - meta_graph.node[s]['timestamp'])
    for n in pred_tree.nodes_iter():
        assert meta_graph.has_node(n), n
    for s, t in pred_tree.edges_iter():
        assert meta_graph.has_edge(s, t), (s, t)
    
    node_color_types = {'tp': 'green',
                        'fn': 'blue',
                        'fp': 'red',
                        'tn': 'gray'}
    edge_color_types = {'tp': 'green',
                        'fn': 'blue',
                        'fp': 'red',
                        'tn': 'gray'}

    def get_style_general(n, true_tree_bool_func, pred_tree_bool_func,
                          style_map):
        if isinstance(n, list) or isinstance(n, tuple):
            true_has, pred_has = (true_tree_bool_func(*n),
                                  pred_tree_bool_func(*n))
        else:
            true_has, pred_has = (true_tree_bool_func(n),
                                  pred_tree_bool_func(n))
        if true_has and pred_has:
            return style_map['tp']
        elif true_has and not pred_has:
            return style_map['fn']
        elif not true_has and pred_has:
            return style_map['fp']
        else:
            return style_map['tn']
        
    root = get_roots(true_tree)[0]
    get_node_color = (lambda n: 'black'
                      if n == root
                      else
                      get_style_general(
                          n,
                          true_tree.has_node,
                          pred_tree.has_node,
                          node_color_types)
    )
    get_edge_color = lambda n: get_style_general(n,
                                                 true_tree.has_edge,
                                                 pred_tree.has_edge,
                                                 edge_color_types)

    if draw_which == "together":
        g = nx.compose(true_tree, pred_tree)
        output_path = '/cs/home/hxiao/public_html/figures/tree_inspection/true_event_vs_pred_event{}.png'.format(output_path_suffix)
    else:
        g = true_tree
        output_path = '/cs/home/hxiao/public_html/figures/tree_inspection/true_event{}.png'.format(output_path_suffix)

    pos = nx.graphviz_layout(g, prog='dot')

    nx.draw(g, pos,
            node_color=map(get_node_color, g.nodes_iter()),
            edge_color=map(get_edge_color, g.edges_iter()),
            node_size=200,
            alpha=0.5,
            arrows=False
    )

    if False:
        edge_label_func = lambda s, t: '{0:.2f}({1:.2f}, {2:.2f})'.format(
            meta_graph[s][t]['c'],
            meta_graph[s][t]['orig_c'],
            meta_graph[s][t]['recency']
        )
    else:
        edge_label_func = lambda s, t: '{0:.2f}'.format(meta_graph[s][t]['c'])

    if True:
        nx.draw_networkx_edge_labels(
            g, pos,
            edge_labels={(s, t): edge_label_func(s, t)
                         for s, t in g.edges_iter()},
            alpha=0.5
        )

    if True:
        nx.draw_networkx_labels(
            g, pos,
            edge_labels={i: str(i) for i in g.nodes()},
            alpha=0.5
        )
        
    plt.savefig(output_path)
if __name__ == '__main__':
    import numpy as np
    np.set_printoptions(precision=2, suppress=True)
    import matplotlib.pyplot as plt
    import cPickle as pkl

    plt.figure(figsize=(8, 8))
    pred_path, mg_path = pkl.load(open('.paths.pkl'))
    true_path = 'data/synthetic_single_tree/events--n_noisy_interactions_fraction=0.0.pkl'
    pred_tree = pkl.load(open(pred_path))[0]
    true_tree = pkl.load(open(true_path))[0]
    
    meta_graph = nx.read_gpickle(mg_path)

    # print('mg.c:', [meta_graph[s][t]['c'] for s, t in true_tree.edges_iter()])
    # print('t.c:', [true_tree[s][t]['c'] for s, t in true_tree.edges_iter()])
    # print 'true_tree.cost', sum(meta_graph[s][t]['c'] for s, t in true_tree.edges_iter())
    # print 'pred_tree.cost', sum(meta_graph[s][t]['c'] for s, t in pred_tree.edges_iter())
    for s, t in true_tree.edges_iter():
        print(s, t, meta_graph[s][t])

    if not True:
        output_path_suffix = '_recency'
    else:
        output_path_suffix = ''

    if True:
        draw_which = 'together'
    else:
        draw_which = 'true_tree'

    draw_pred_tree_against_true_tree(pred_tree, true_tree, meta_graph,
                                     draw_which=draw_which,
                                     output_path_suffix=output_path_suffix)

