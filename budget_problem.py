import networkx as nx
import math
from copy import copy

from tree_util import tree_density
from util import memoized


def transitive_closure(g, node_weight='p', edge_weight='c'):
    new_g = nx.DiGraph()
    l = nx.all_pairs_dijkstra_path_length(g, weight=edge_weight)
    # add shortest path and weight
    new_g.add_edges_from([
        (s, tree, {edge_weight: l[s][tree]})
        for s in l for tree in l[s]]
    )
    # add node weight
    for n in new_g.nodes_iter():
        new_g.node[n][node_weight] = g.node[n][node_weight]
    return new_g, nx.all_pairs_dijkstra_path(g, weight=edge_weight)


@memoized
def charikar_algo(g, root, terminals, k, level):
    """
    d: terminals
    """
    assert level >= 1
    # make the graph into transitive closure
    g_tc, sp_table = transitive_closure(g)
    
    # convert terminals to set if necessary
    if not isinstance(terminals, set):
        terminals = set(terminals)

    def aux(r, X, k, l):
        X = copy(X)

        reachable_from_r = nx.descendants(g, r)
        X_p = set(reachable_from_r).intersection(X)

        if len(X_p) < k:
            return nx.DiGraph()

        if k == 1 and r in X:
            tree = nx.DiGraph()
            tree.add_node(r)
            return tree
        elif l == 1:
            selected_X = sorted(
                X_p,
                key=lambda n: g_tc[r][n]['c']
            )[:k]
            tree = nx.DiGraph()
            for x in selected_X:
                tree.add_path(sp_table[r][x])
            # add edge cost
            for u, v in tree.edges_iter():
                tree[u][v]['c'] = g_tc[u][v]['c']
            return tree
        else:
            sub_trees = []
            while k > 0:
                # if l ==3:
                #     print('---'*10)
                t_best = None
                density_best = float('inf')
                for v in reachable_from_r:
                    for k_p in range(1, k+1):
                        tree = aux(v, X, k_p, l-1)
                        # if l == 3:
                        #     print('after aux, X:', X)
                        for s, t in zip(sp_table[r][v][:-1],
                                        sp_table[r][v][1:]):
                            tree.add_edge(s, t, {'c': g[s][t]['c']})
                        density_new = tree_density(tree, X)
                        if density_best > density_new:
                            t_best = tree
                            density_best = density_new
                            # if l == 3:
                            #     print('root:', v)
                            #     print('X:', X)
                            #     print('k_p:', k_p)
                            #     print('l:', l-1)
                            #     print('tree:', tree.nodes())
                            #     print('density: {}'.format(density_new))
                assert t_best is not None
                sub_trees.append(t_best)
                # if l == 3:
                #     print('***'*10)
                #     print(t_best.nodes())
                #     print(X)
                reached_X = set(t_best.nodes()).intersection(X)
                k -= len(reached_X)
                X -= reached_X
                # if l == 3:
                #     print('t_best.nodes():', t_best.nodes())
                #     print('update on X, k:')
                #     print('reached_X:', reached_X)
                #     print('X:', X)
                #     print('k:', k)
                #     print('***'*10)
            return reduce(nx.compose, sub_trees, nx.DiGraph())

    return aux(root, terminals, k, level)


def binary_search_using_charikar(g, root, B, level,
                                 cost_key='c'):
    """
    works for the problem, budgeted k-minimum spanning tree,
    thus, node prize are uniform
    """
    g_cost = lambda t: sum(t[u][v][cost_key]
                           for u, v in t.edges_iter())
    Q_l = 1.  # feasible for sure
    Q_u = g.number_of_nodes()  # might be feasible

    lastest_feasible_t = None
    terminals = tuple(g.nodes())  # make it memoizable
    
    while Q_l < Q_u - 1:
        Q = int(math.floor((Q_l + Q_u) / 2.))
        # print('Q:', Q)
        t = charikar_algo(g, root, terminals, Q, level)

        assert(len(terminals) == g.number_of_nodes())

        cost = g_cost(t)
        # print('cost, B:', cost, B)
        if cost > B:
            Q_u = Q - 1
        elif cost < B:
            if set(t.nodes()) == set(g.nodes()):
                # all nodes are included
                return t
            lastest_feasible_t = t
            Q_l = Q
        else:
            return t
    
    t_p = charikar_algo(g, root, terminals, Q_u, level)
    # print('Q_u, cost(t_p):', Q_u, g_cost(t_p))
    if g_cost(t_p) < B:
        return t_p
    else:
        if lastest_feasible_t is None:
            return charikar_algo(g, root, terminals, Q_l, level)
        else:
            return lastest_feasible_t
