# Convert a list of interactions into a meta interaction graph

import ujson as json
import networkx as nt
from collections import defaultdict


class MetaGraph(object):

    @classmethod
    def convert_enron(cls, node_names, sources, targets, time_stamps):
        """
        sources: list of source node id for each interaction
        targets: list of target node ids for each interaction
        time_stamps: happening time of the interactions

        All four fields shall be sorted from earliest to lastest
        according to time_stamps
        """
        assert len(node_names) == len(sources) == len(targets) == len(time_stamps)
        g = nt.DiGraph()
        
        s2n = defaultdict(set)  # source to nodes mapping
        for n, s in zip(node_names, sources):
            s2n[s].add(n)
        
        for n1, s, ts in zip(node_names, sources, targets):
            # remove entries of n1 in s2n
            s2n[s].remove(n1)

            # add edges
            for n2 in s2n[s]:
                g.add_edge(n1, n2)
            for t in ts:
                for n2 in s2n[t]:
                    g.add_edge(n1, n2)
        return g
