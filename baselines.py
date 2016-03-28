import networkx as nx
import random
import numpy as np

# @profile
def new_frontier(new_node, selected_nodes, g, current_frontier):
    """get the frontier edges that can be selected
    """
    selected_nodes = set(selected_nodes)
    frontier = set(current_frontier)
    for n in selected_nodes:
        frontier -=  {(n, new_node)}
        # e = (n, new_node)
        # if e in frontier:
        #     frontier.remove(e)

    for nbr in g.neighbors_iter(new_node):
        if nbr not in selected_nodes:
            frontier.add((new_node, nbr))
    return list(frontier)

# @profile
def greedy_choice_by_cost(g, edges,
                          edge_cost_key,
                          node_reward_key):
    return min(edges,
               key=lambda e: g[e[0]][e[1]][edge_cost_key])

# @profile
def greedy_choice_by_cost_numpy(g, edges,
                                edge_cost_key,
                                node_reward_key):
    costs = np.asarray([g[s][t][edge_cost_key] for s, t in edges])
    return edges[np.argmin(costs)]


# @profile
def greedy_choice_by_discounted_reward(
        g, edges,
        edge_cost_key, node_reward_key):
    return max(edges,
               key=lambda e:
               (
                   float(g.node[e[1]][node_reward_key]) /
                   g[e[0]][e[1]][edge_cost_key]
                   if g[e[0]][e[1]][edge_cost_key] > 0
                   else float('inf'))
    )


def random_choice(g, edges, edge_cost_key, node_reward_key):
    return random.choice(edges)


# @profile
def grow_tree_general(g, r, U, choose_edge,
                      edge_cost_key='c',
                      node_reward_key='r'):
    """grows a tree by randomly selecting edges
    """
    t = nx.DiGraph()
    cost_sum = 0
    frontier = new_frontier(r, t.nodes(), g, [])
    last_added_edge = None

    while cost_sum <= U and len(frontier) > 0:
        e = choose_edge(g, frontier,
                        edge_cost_key,
                        node_reward_key)
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
        t.remove_node(last_added_edge[1])
    return t

greedy_grow = lambda g, r, U: grow_tree_general(g, r, U,
                                                greedy_choice_by_cost)
greedy_grow_numpy = lambda g, r, U: grow_tree_general(g, r, U,
                                                      greedy_choice_by_cost_numpy)
random_grow = lambda g, r, U: grow_tree_general(g, r, U,
                                                random_choice)


def greedy_grow_by_discounted_reward(g, r, U):
    return grow_tree_general(
        g, r, U,
        greedy_choice_by_discounted_reward)
