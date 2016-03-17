import networkx as nx
import math
from sampler import quota_upperbound

from tree_util import tree_density
from util import memoized


def transitive_closure(g, node_weight='r', edge_weight='c'):
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

    @memoized
    def aux(r, X, k, l):
        """
        X should be tuple in order to be memoizable
        """
        X = set(X)

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
                t_best = None
                density_best = float('inf')
                for v in reachable_from_r:
                    for k_p in range(1, k+1):
                        tree = aux(v, tuple(sorted(list(X))), k_p, l-1)

                        for s, t in zip(sp_table[r][v][:-1],
                                        sp_table[r][v][1:]):
                            tree.add_edge(s, t, {'c': g[s][t]['c']})
                        density_new = tree_density(tree, X)
                        if density_best > density_new:
                            t_best = tree
                            density_best = density_new
                # assert t_best is not None
                # assert nx.is_arborescence(t_best)
                sub_trees.append(t_best)

                reached_X = set(t_best.nodes()).intersection(X)
                # print('X:', X)
                # print('k:', k)
                # print('reached_X:', reached_X)
                # print('t_best:', t_best.edges())
                k -= len(reached_X)
                X -= reached_X
            
            t = reduce(nx.compose, sub_trees, nx.DiGraph())
            # for n in t.nodes_iter():
            #     if t.in_degree(n) > 1:
            #         print('n:', n)
            # assert nx.is_arborescence(t)
            return t
    dag = aux(root, tuple(sorted(list(terminals))), k, level)

    # remove redundant edges
    # to make it tree
    edges_to_remove = set()
    for n in dag.nodes_iter():
        if dag.in_degree(n) > 1:
            in_edges = dag.in_edges(n)
            min_cost_edge = min(
                in_edges,
                key=lambda (s, t): dag[s][t]['c']
            )
            edges_to_remove |= (set(in_edges) - {min_cost_edge})
    dag.remove_edges_from(edges_to_remove)
    return dag


def binary_search_using_charikar(g, root, B, level,
                                 cost_key='c'):
    """
    works for the problem, budgeted k-minimum spanning tree,
    thus, node prize are uniform
    """
    paths = transitive_closure(g)[1][root]
    depth = max(len(p) for p in paths.values())
    print('depth:', depth)
    print('root:', root)
    g_cost = lambda t: sum(t[u][v][cost_key]
                           for u, v in t.edges_iter())
    Q_l = 1.  # feasible for sure
    print('B:', B)
    print('quota_ub:', quota_upperbound(g, root, B))
    Q_u = quota_upperbound(g, root, B)  # might be feasible

    lastest_feasible_t = None
    terminals = g.nodes()
    
    while Q_l < Q_u - 1:
        Q = int(math.floor((Q_l + Q_u) / 2.))
        print('Q_l, Q_u, Q:', Q_l, Q_u, Q)
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
