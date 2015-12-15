# Convert a list of interactions into a meta interaction graph

import networkx as nt

from collections import defaultdict

import logging
logger = logging.getLogger("convert_to_meta_graph")
logger.setLevel(logging.INFO)


def convert_to_meta_graph(interaction_names, sources, targets, time_stamps):
    """
    sources: list of source node id for each interaction
    targets: list of target node ids for each interaction
    time_stamps: happening time of the interactions

    All four fields shall be sorted from earliest to lastest
    according to time_stamps
    """
    assert len(interaction_names) == len(sources) == len(targets) == len(time_stamps), \
        "{},{},{},{}".format(len(interaction_names), len(sources), len(targets), len(time_stamps))
    g = nt.DiGraph()
    
    # source to nodes mapping
    # interpretation:
    # s is associated with a list of interactions that take it as source
    s2i = defaultdict(set)

    for i, s, time in zip(interaction_names, sources, time_stamps):
        if (i, time) in s2i[s]:
            logger.warning("{} added already".format((i, time)))
        else:
            s2i[s].add((i, time))

    for i1, s, ts, time1 in zip(
            interaction_names, sources, targets, time_stamps):
        # remove entries of i1 in s2i
        s2i[s].remove((i1, time1))

        # add node, can be singleton
        g.add_node(i1)
        
        # add edges
        # broadcast pattern
        for i2, time2 in s2i[s]:
            if time1 < time2:
                g.add_edge(i1, i2)
        # relay pattern
        for t in ts:
            for i2, time2 in s2i[t]:
                if time1 < time2:
                    g.add_edge(i1, i2)
    return g
    

def convert_to_original_graph(mg):
    g = nt.DiGraph()
    for n in mg.nodes():
        sender = mg.node[n]['sender_id']
        for recipient in mg.node[n]['recipient_ids']:
            g.add_edge(sender, recipient)
    return g
