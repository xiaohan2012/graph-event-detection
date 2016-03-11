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


def draw_pred_tree_against_true_tree(pred_tree, true_tree, meta_graph):
    """
    Draw predicted event against the true event
    while using the meta graph as the background
    """
    for n in true_tree.nodes_iter():
        assert meta_graph.has_node(n)
    
    node_color_types = {'tp': 'green',
                        'fn': 'blue',
                        'fp': 'red',
                        'tn': 'gray'}
    edge_color_types = {'tp': 'green',
                        'fn': 'blue',
                        'fp': 'red',
                        'tn': 'gray'}
    # edge_alpha_types = {'tp': 1.0,
    #                     'fn': 1.0,
    #                     'fp': 1.0,
    #                     'tn': 0.2}

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
    # pos = nx.spring_layout(meta_graph, k=1.0)
    pos = nx.graphviz_layout(meta_graph, prog='dot')
    nx.draw(meta_graph, pos,
            node_color=map(get_node_color, meta_graph.nodes_iter()),
            edge_color=map(get_edge_color, meta_graph.edges_iter()),
            node_size=100,
            alpha=0.5,
            arrows=False
    )


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cPickle as pkl

    plt.figure(figsize=(8, 8))
    pred_path = 'tmp/synthetic_single_tree/result/result--fraction=0.2--greedy--U=34.0728347028--dijkstra=False--timespan=100.28206487----apply_pagerank=False--dist_func=cosine--distance_weights={"topics":1.0}--preprune_secs=100.28206487----cand_tree_percent=0.1--root_sampling=uniform.pkl'
    true_path = 'data/synthetic_single_tree/events--n_noisy_interactions_fraction=0.2.pkl'
    mg_path = 'tmp/synthetic_single_tree/meta-graph--apply_pagerank=False--dist_func=cosine--distance_weights={"topics":1.0}--preprune_secs=100.28206487.pkl'

    pred_tree = pkl.load(open(pred_path))[0]
    true_tree = pkl.load(open(true_path))[0]
    # meta_graph = nx.read_gpickle(mg_path)
    meta_graph = nx.compose(pred_tree, true_tree)
    # meta_graph = true_treep

    draw_pred_tree_against_true_tree(pred_tree, true_tree, meta_graph)

    plt.savefig('/cs/home/hxiao/public_html/figures/tree_inspection/true_event_vs_pred_event.png')
