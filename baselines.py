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
        t.add_edge(*e)
        frontier = new_frontier(e[1], t.nodes(), g, frontier)
        last_added_edge = e
        cost_sum += g[e[0]][e[1]][edge_cost_key]

    if cost_sum > U:
        t.remove_edge(*last_added_edge)
    return t
        
