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
        print('eps: ', eps)
        if eps_1 < eps_2:
            print('chose edge ({}, {})'.format(*edge))
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
            print('deactivate {})'.format(min_c, ))
            # deactivate
            lmbd[min_c] = 0
            for v in min_c:
                if labels[v] is None:
                    labels[v] = min_c
        
    t = nx.DiGraph()
    t.add_edges_from(F)
    
    edges = t.edges()
    for i, j in edges:
        if not nx.has_path(g, r, j):
            t.remove_edge(i, j)
    return t, list(set(g.nodes()) - set(t.nodes()))

