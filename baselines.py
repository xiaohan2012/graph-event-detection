import networkx as nx
import random
from copy import deepcopy


def new_frontier(new_node, selected_nodes, g, current_frontier):
    """get the frontier edges that can be selected
    """
    selected_nodes = set(selected_nodes)
    frontier = set(deepcopy(current_frontier))
    for n in selected_nodes:
        e = (n, new_node)
        if e in frontier:
            frontier.remove(e)

    for nbr in g.neighbors(new_node):
        if nbr not in selected_nodes:
            e = (new_node, nbr)
            frontier.add(e)
    return list(frontier)


def greedy_choice_by_cost(g, edges, edge_cost_key='c'):
    return min(edges,
               key=lambda e: g[e[0]][e[1]][edge_cost_key])


def random_choice(g, edges, edge_cost_key='c'):
    return random.choice(edges)


def grow_tree_general(g, r, U, choose_edge, edge_cost_key='c'):
    """grows a tree by randomly selecting edges
    """
    t = nx.DiGraph()
    cost_sum = 0
    frontier = new_frontier(r, t.nodes(), g, [])
    last_added_edge = None

    while cost_sum <= U and len(frontier) > 0:
        e = choose_edge(g, frontier)
        u, v = e
        t.add_edge(*e)
        frontier = new_frontier(v, t.nodes(), g, frontier)
        last_added_edge = e
        cost_sum += g[u][v][edge_cost_key]

        # copy attributes
        t[u][v] = g[u][v]
        t.node[u] = g.node[u]
        t.node[v] = g.node[v]
    if cost_sum > U:
        t.remove_edge(*last_added_edge)
    return t

greedy_grow = lambda g, r, U: grow_tree_general(g, r, U,
                                                greedy_choice_by_cost)
random_grow = lambda g, r, U: grow_tree_general(g, r, U,
                                                random_choice)