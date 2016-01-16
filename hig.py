# Heterogeneous Interaction Graph(HIG) construction

import networkx as nx
import itertools


def construct_hig_from_interactions(interactions,
                                    take_largest_component=True):
    """
    If multiple connected components exist in the hig,
    pagerank may produce bad results, for example:
    page rank score for nodes in small connected compoent is high.
    """
    # some check
    user_ids = set([i['sender_id'] for i in interactions])
    user_ids |= set(itertools.chain(
        *[i['recipient_ids'] for i in interactions]
    ))
    message_ids = set([i['message_id'] for i in interactions])
    
    if user_ids.intersection(message_ids):
        raise ValueError('user_ids shouldn\'t intersect with message_ids')

    g = nx.DiGraph()
    
    for i in interactions:
        mid = i['message_id']
        g.add_edge(i['sender_id'], mid)
        for recipient in i['recipient_ids']:
            g.add_edge(mid, recipient)
    
    if take_largest_component:
        # remove nodes
        # that are disconnected from the largest connected component
        subgraphs = nx.connected_component_subgraphs(g.to_undirected())
        disconnected_subgraphs = sorted(
            subgraphs,
            key=lambda sub_g: len(sub_g),
            reverse=True
        )[1:]
        nodes_to_remove = itertools.chain(
            *[sub_g.nodes() for sub_g in disconnected_subgraphs]
        )
        g.remove_nodes_from(nodes_to_remove)
        assert len(
            list(nx.connected_component_subgraphs(g.to_undirected()))
        ) == 1
    return g
