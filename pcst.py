import numpy as np
import networkx as nx


def pcst_greedy(g, r):
    """
    edge cost key: 'c'
    node penalty key: 'p'
    """
    F = set()
    C = set()
    Ct = {}
    d = {}
    lmbd = {}
    w = {}
    labels = {}
    for v in g.nodes_iter():
        C.add((v,))
        Ct[(v,)] = v
        d[v] = 0
        lmbd[(v,)] = (1 if v != r else 0)
        w[(v,)] = 0
        labels[v] = None
    
    while True:
        any_active_component = np.array([lmbd[c] for c in C]).any()
        if not any_active_component:
            break
        eps_1 = float('inf')
        min_cp, min_cq, edge, min_root = None, None, None, None

        for cp in C:
            for cq in C:
                if cp != cq:
                    for i in cp:
                        j = Ct[cq]
                        if g.has_edge(i, j):
                            if lmbd[cq] == 1:
                                tmp = g[i][j]['c'] - d[j]
                                if eps_1 > tmp:
                                    eps_1 = tmp
                                    edge = (i, j)
                                    min_cp = cp
                                    min_cq = cq
                                    min_root = Ct[cp]
                    
        eps_2 = float('inf')
        for c in C:
            if lmbd[c] == 1:
                tmp = sum([g.node[i]['p'] for i in c]) - w[c]
                if tmp < eps_2:
                    eps_2 = tmp
                    min_c = c

        eps = min(eps_1, eps_2)

        for c in C:
            if lmbd[c]:
                w[c] += eps
                d[Ct[c]] += eps
        # print('eps: ', eps)
        if eps_1 < eps_2:
            # print('chose edge ({}, {})'.format(*edge))
            # merge two components
            F.add(edge)
            C.remove(min_cp)
            C.remove(min_cq)
            c = min_cp + min_cq
            C.add(c)
            
            Ct[c] = min_root
            w[c] = w[min_cp] + w[min_cq]
            lmbd[c] = (0 if r in c else 1)
        else:
            # print('deactivate {})'.format(min_c, ))
            # deactivate
            lmbd[min_c] = 0
            for v in min_c:
                if labels[v] is None:
                    labels[v] = min_c
        
    t = nx.DiGraph()
    t.add_edges_from(F)
    for n in t.nodes_iter():
        t.node[n]['p'] = g.node[n]['p']
    for i, j in t.edges_iter():
        t[i][j]['c'] = g[i][j]['c']
    
    edges = t.edges()
    for i, j in edges:
        if not nx.has_path(t, r, j):
            t.remove_edge(i, j)

    nodes = t.nodes()
    for n in nodes:
        if t.degree(n) == 0:
            t.remove_node(n)

    return t, list(set(g.nodes()) - set(t.nodes()))


def solve_budget_using_binary_search(g, r, B, eps=0.1):
    """node reward are uniform
    """
    graph_edge_cost = lambda g: sum(
        (g[i][j]['c'] for i, j in g.edges_iter())
    )
    edge_cost_sum = graph_edge_cost(g)
    lmbd1, lmbd2 = 0, edge_cost_sum
    cost = edge_cost_sum

    while np.abs(lmbd2 - lmbd1) > eps:
        lmbd = np.mean([lmbd1, lmbd2])
        # print('lambda: ', lmbd)
        for n in g.nodes_iter():
            g.node[n]['p'] = lmbd
        t, x = pcst_greedy(g, r)
        cost = graph_edge_cost(t)

        reward = sum(g.node[n]['p'] for n in t.nodes_iter())
        # print('cost:', cost)
        # print('reward:', reward / lmbd)
        # print()
        
        if cost > B:
            lmbd2 = lmbd
        elif cost < B:
            lmbd1 = lmbd
        else:
            return t
    return t
