# Convert a list of interactions into a meta interaction graph

import networkx as nt
from collections import defaultdict


def convert_to_meta_graph(node_names, sources, targets, time_stamps):
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

            # add node, can be singleton
            g.add_node(n1)
            
            # add edges
            for n2 in s2n[s]:
                g.add_edge(n1, n2)
            for t in ts:
                for n2 in s2n[t]:
                    g.add_edge(n1, n2)
        return g


class EnronUtil(object):
    @classmethod
    def get_meta_graph(cls, interactions):
        """
        Return the meta graph together with temporally sorted interactions
        """
        interactions = sorted(interactions, key=lambda r: r['datetime'])
        node_names = [i['message_id'] for i in interactions]
        sources = [i['sender_id'] for i in interactions]
        targets = [i['recipient_ids'] for i in interactions]
        time_stamps = [i['datetime'] for i in interactions]
        
        g = convert_to_meta_graph(node_names, sources,
                                  targets, time_stamps)
        for i in interactions:
            n = i['message_id']
            g.node[n]['body'] = i['body']
            g.node[n]['subject'] = i['subject']

        return (g, interactions)
    


