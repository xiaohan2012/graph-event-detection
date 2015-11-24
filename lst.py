from collections import defaultdict

from networkx.classes.digraph import DiGraph
from networkx.algorithms.dag import topological_sort


def lst_dag(G, r, U,
            node_reward_key='r',
            edge_cost_key='c',
            debug=False):
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
        A[n][0] = G.node[n][node_reward_key]

        D[n] = {}  # set of nodes included corresponding to A[u][i]
        D[n][0] = {n}

        BP[n] = defaultdict(list)  # backpointer corresponding to A[u][i]
    for n in topological_sort(G, reverse=True):  # leaves come first
        children = G.neighbors(n)
        reward = G.node[n][node_reward_key]
        if len(children) == 1:
            child = children[0]
            w = G[n][child][edge_cost_key]
            for i in xrange(U, w - 1, -1):
                if (i-w) in A[child]:
                    A[n][i] = A[child][i-w] + reward
                    D[n][i] = D[child][i-w] | {n}
                    BP[n][i] = [(child, i-w)]
        elif len(children) > 1:
            assert len(children) == 2
            lchild, rchild = children
            lw = G[n][lchild][edge_cost_key]
            rw = G[n][rchild][edge_cost_key]

            for i in xrange(U, min(lw, rw) - 1, -1):
                max_val = float('-inf')
                max_nodes = None
                prev = None

                if i - lw >= 0 and (i - lw) in A[lchild]:
                    max_val = A[lchild][i - lw] + reward
                    max_nodes = D[lchild][i - lw] | {n}
                    prev = [(lchild, i - lw)]
                
                if (i - rw >= 0
                    and (i - rw) in A[rchild]
                    and A[rchild][i - rw] + reward > max_val):
                    max_val = A[rchild][i - rw] + reward
                    max_nodes = D[rchild][i - rw] | {n}
                    prev = [(rchild, i - rw)]

                for j in xrange(i - lw - rw, -1, -1):
                    if j in A[lchild] and (i-j-lw-rw) in A[rchild]:
                        val = A[lchild][j] + A[rchild][i-j-lw-rw] + reward
                        lset, rset = D[lchild][j], D[rchild][i-j-lw-rw]
                        if val > max_val and len(lset & rset) == 0:
                            max_val = val
                            max_nodes = lset | rset | {n}
                            prev = [(lchild, j), (rchild, i-j-lw-rw)]

                if max_nodes != None:
                    # we should have at least one *feasible* solution
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
