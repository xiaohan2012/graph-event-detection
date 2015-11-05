from collections import defaultdict

from networkx.classes.digraph import DiGraph
from networkx.algorithms.dag import topological_sort


def lst_dag(G, r, U, debug=False):
    """
    Param:
    -------------
    binary_dag: a DAG in networkx format. Each node can have at most 2 child
    r: root node in dag
    U: the maximum threshold of edge weight sum

    Return:
    maximum-sum subtree rooted at r whose sum of edge weights <= A
    ------------
    """
    ns = G.nodes()
    A, D, BP = {}, {}, {}
    for n in ns:
        A[n] = {}  # maximum sum of node u at a cost i
        A[n][0] = 1

        D[n] = {}  # set of nodes included corresponding to A[u][i]
        D[n][0] = {n}

        BP[n] = defaultdict(list)  # backpointer corresponding to A[u][i]

    for n in topological_sort(G, reverse=True):  # leaves come first
        children = G.neighbors(n)
        if len(children) == 1:
            child = children[0]
            w = G[n][child]['w']
            for i in xrange(U, w - 1, -1):
                if (i-w) in A[child]:
                    A[n][i] = A[child][i-w] + 1
                    D[n][i] = D[child][i-w] | {n}
                    BP[n][i] = [(child, i-w)]
        elif len(children) > 1:
            assert len(children) == 2
            lchild, rchild = children
            lw = G[n][lchild]['w']
            rw = G[n][rchild]['w']

            for i in xrange(U, min(lw, rw) - 1, -1):
                max_val = float('-inf')
                max_nodes = None
                prev = None

                if i - lw >= 0 and (i - lw) in A[lchild]:
                    max_val = A[lchild][i - lw] + 1
                    max_nodes = D[lchild][i - lw] | {n}
                    prev = [(lchild, i - lw)]
                
                if (i - rw >= 0
                    and (i - rw) in A[rchild]
                    and A[rchild][i - rw] + 1 > max_val):
                    max_val = A[rchild][i - rw] + 1
                    max_nodes = D[rchild][i - rw] | {n}
                    prev = [(rchild, i - rw)]

                for j in xrange(i - lw - rw, -1, -1):
                    if j in A[lchild] and (i-j-lw-rw) in A[rchild]:
                        val = A[lchild][j] + A[rchild][i-j-lw-rw] + 1
                        lset, rset = D[lchild][j], D[rchild][i-j-lw-rw]
                        if val > max_val and len(lset & rset) == 0:
                            max_val = val
                            max_nodes = lset | rset | {n}
                            prev = [(lchild, j), (rchild, i-j-lw-rw)]
                A[n][i] = max_val
                D[n][i] = max_nodes
                BP[n][i] = prev
            if n == r:  # no need to continue once we processed root
                break

    best_cost = max(xrange(U + 1),
                    key=lambda i: A[r][i] if i in A[r] else float('-inf'))
    tree = DiGraph()
    stack = []
    for n, cost in BP[r][best_cost]:
        stack.append((r, n, cost))
    while len(stack) > 0:
        parent, child, cost = stack.pop(0)
        tree.add_edge(parent, child)
        for grandchild, cost2 in BP[child][cost]:
            stack.append((child, grandchild, cost2))
    return tree


def nw_lst_dag(G, r, U, debug=False):
    """
    length-constrained maximum-sum tree for DAG with nw(node weights)
    Param:
    -------------
    binary_dag: a DAG in networkx format. Each node can have at most 2 child
    r: root node in dag
    U: the maximum threshold of edge weight sum

    Return:
    maximum-sum subtree rooted at r whose sum of edge weights <= A
    ------------
    """
    ns = G.nodes()
    A, D, BP = {}, {}, {}
    for n in ns:
        A[n] = {}  # maximum sum of node u at a cost i
        D[n] = {}  # set of nodes included corresponding to A[u][i]

        w = G.node[n]['w']
        if w <= U:
            A[n][w] = 1
            D[n][w] = {n}

        BP[n] = defaultdict(list)  # backpointer corresponding to A[u][i]

    for n in topological_sort(G, reverse=True):  # leaves come first
        children = G.neighbors(n)  # children
        if len(children) == 1:
            child = children[0]
            w = G.node[n]['w' ]
            for i in xrange(U, w - 1, -1):
                if (i-w) in A[child]:
                    A[n][i] = A[child][i-w] + 1
                    D[n][i] = D[child][i-w] | {n}
                    BP[n][i] = [(child, i-w)]
        elif len(children) > 1:
            assert len(children) == 2
            lchild, rchild = children
            w = G.node[n]['w']

            for i in xrange(U, w - 1, -1):
                max_val = float('-inf')
                max_nodes = None
                prev = None

                if i - w >= 0 and (i - w) in A[lchild]:
                    max_val = A[lchild][i - w] + 1
                    max_nodes = D[lchild][i - w] | {n}
                    prev = [(lchild, i - w)]
                
                if (i - w >= 0
                    and (i - w) in A[rchild]
                    and A[rchild][i - w] + 1 > max_val):
                    max_val = A[rchild][i - w] + 1
                    max_nodes = D[rchild][i - w] | {n}
                    prev = [(rchild, i - w)]

                for j in xrange(i - w, -1, -1):
                    if j in A[lchild] and (i-j-w) in A[rchild]:
                        val = A[lchild][j] + A[rchild][i-j-w] + 1
                        lset, rset = D[lchild][j], D[rchild][i-j-w]
                        if val > max_val and len(lset & rset) == 0:
                            max_val = val
                            max_nodes = lset | rset | {n}
                            prev = [(lchild, j), (rchild, i-j-w)]
                A[n][i] = max_val
                D[n][i] = max_nodes
                BP[n][i] = prev
            if n == r:  # no need to continue once we processed root
                break

    best_cost = max(xrange(U + 1),
                    key=lambda i: A[r][i] if i in A[r] else float('-inf'))
    tree = DiGraph()
    stack = []
    for n, cost in BP[r][best_cost]:
        stack.append((r, n, cost))
    while len(stack) > 0:
        parent, child, cost = stack.pop(0)
        tree.add_edge(parent, child)
        for grandchild, cost2 in BP[child][cost]:
            stack.append((child, grandchild, cost2))
    return tree
