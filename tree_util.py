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
