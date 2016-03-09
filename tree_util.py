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
    assert nx.is_arborescence(tree)
    return aux(get_roots(tree)[0])
    

JAR_PATH = make_path('external/APTED-0.1.1.jar')


def salzburg_ted(tree1, tree2):
    """
    tree edit distance

    From [Source](tree-edit-distance.dbresearch.uni-salzburg.at/#download)
    """
    print(to_bracket_notation(tree1))
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
