import networkx as nx
from copy import copy
from tree_util import tree_density


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


def tree_cover(tree, B):
    """
    Split the tree into a set of subtrees such that each of them has [B/2, B] cost
    """


def binary_search_using_charikar(tree, root, B, epsilon, max_level):
    """
    Suppose `OPT` is the optimal value for the budget problem with `B`. If `Q <= OPT`, `c(T) <= \alpha B `. Thus, we increase `Q` geometrically as long as it stays under the bound. So finally `OPT/(1+\epsilon) <= Q <= OPT`. For the resulting tree `T`, we can split into `N` subtrees such that they cover `T` and the average cost of subtree stays between `[B/2, B]`. Thus there can be at most `\beta = 2 * floor(\alpha) + round(mod(\alpha), 1)` subtrees and their reward is at least `OPT / (1+\epsilon) / \beta`.
    """
    pass
