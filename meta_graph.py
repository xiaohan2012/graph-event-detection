# Convert a list of interactions into a meta interaction graph

import networkx as nt

from collections import defaultdict
from memory_profiler import profile
from itertools import izip

import logging
logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("convert_to_meta_graph")
logger.setLevel(logging.DEBUG)

def convert_to_meta_graph(interaction_names, sources,
                          targets, time_stamps,
                          preprune_secs=None):
    """
    sources: list of source node id for each interaction
    targets: list of target node ids for each interaction
    time_stamps: happening time of the interactions

    All four fields shall be sorted from earliest to lastest
    according to time_stamps
    """
    if isinstance(preprune_secs, int) or isinstance(preprune_secs, float):
        logger.info("preprune_by_secs {} enabled..".format(preprune_secs))
    else:
        if preprune_secs is not None:
            raise TypeError(
                'preprune_secs should be int or float, is {}'.format(
                    type(preprune_secs)
                )
            )

    assert len(interaction_names) == len(sources) == len(targets) == len(time_stamps), \
        "{},{},{},{}".format(len(interaction_names), len(sources), len(targets), len(time_stamps))
    g = nt.DiGraph()
    
    # source to nodes mapping
    # interpretation:
    # s is associated with a list of interactions that take it as source
    s2i = defaultdict(set)

    for row_n, (i, s, time) in enumerate(izip(interaction_names, sources, time_stamps)):
        if (i, time) in s2i[s]:
            logger.warning("{} added already".format((i, time)))
        else:
            s2i[s].add((i, time))

    for row_n, (i1, s, ts, time1) in enumerate(izip(
            interaction_names, sources, targets, time_stamps)):
        if row_n % 5000 == 0:
            logger.debug("building: {} / {}".format(row_n, len(interaction_names)))

        # remove entries of i1 in s2i
        s2i[s].remove((i1, time1))

        # add node, can be singleton
        g.add_node(i1)
        
        # add edges
        # broadcast pattern
        for i2, time2 in s2i[s]:
            if time1 < time2:
                if (preprune_secs is None or
                    time2 - time1 <= preprune_secs):
                    g.add_edge(i1, i2)
        # relay pattern
        for t in ts:
            for i2, time2 in s2i[t]:
                if time1 < time2:
                    if (preprune_secs is None or
                        time2 - time1 <= preprune_secs):
                        g.add_edge(i1, i2)
    return g
    

def convert_to_original_graph(mg):
    g = nt.DiGraph()
    for n in mg.nodes():
        sender = mg.node[n]['sender_id']
        for recipient in mg.node[n]['recipient_ids']:
            g.add_edge(sender, recipient)
    return g
