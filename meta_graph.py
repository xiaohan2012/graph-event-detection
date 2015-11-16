# Convert a list of interactions into a meta interaction graph

import re
import numpy as np
import nltk
import networkx as nt

from datetime import datetime
from collections import defaultdict

from util import load_items_by_line


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
        s2i[s].add((i, time))
    
    for i1, s, ts, time1 in zip(
            interaction_names, sources, targets, time_stamps):
        # remove entries of i1 in s2i
        s2i[s].remove((i1, time1))

        # add node, can be singleton
        g.add_node(i1)
        
        # add edges
        for i2, time2 in s2i[s]:
            if time1 < time2:
                g.add_edge(i1, i2)
        for t in ts:
            for i2, time2 in s2i[t]:
                if time1 < time2:
                    g.add_edge(i1, i2)
    return g


class EnronUtil(object):
    stoplist = load_items_by_line('lemur-stopwords.txt')
    valid_token_regexp = re.compile('^[a-z]+$')

    @classmethod
    def get_meta_graph(cls, interactions):
        """
        Return the meta graph together with temporally sorted interactions
        """
        interactions = sorted(interactions, key=lambda r: r['datetime'])
        interaction_names = [i['message_id'] for i in interactions]
        sources = [i['sender_id'] for i in interactions]
        targets = [i['recipient_ids'] for i in interactions]
        time_stamps = [i['datetime'] for i in interactions]
        
        g = convert_to_meta_graph(interaction_names, sources,
                                  targets, time_stamps)
        for i in interactions:
            n = i['message_id']
            g.node[n]['body'] = i['body']
            g.node[n]['subject'] = i['subject']
            g.node[n]['timestamp'] = i['datetime']
            g.node[n]['datetime'] = datetime.fromtimestamp(i['datetime'])
            
        return g

    @classmethod
    def tokenize_document(cls, doc):
        return [
            word for word in nltk.word_tokenize(doc.lower())
            if (word not in cls.stoplist and
                cls.valid_token_regexp.match(word) and
                len(word) > 2)
        ]

    @classmethod
    def add_topics_to_graph(cls, g, lda_model, dictionary):
        for n in g.nodes():
            doc = u'{} {}'.format(g.node[n]['subject'], g.node[n]['body'])
            topic_dist = lda_model.get_document_topics(
                dictionary.doc2bow(cls.tokenize_document(doc)),
                minimum_probability=0
            )
            g.node[n]['topics'] = np.asarray([v for _, v in topic_dist],
                                             dtype=np.float)
            
        return g

    @classmethod
    def filter_dag_given_root(cls, g, r, filter_func):
        """filter nodes given root and some filter function

        Return:
        a DAG, sub_g of which all nodes in sub_g passes filter_func
        """
        sub_g = nt.DiGraph()
        stack = [(r, child) for child in g.neighbors(r)]
        while len(stack) > 0:
            parent, child = stack.pop()
            if filter_func(child):
                sub_g.add_edge(parent, child)
                for grand_child in g.neighbors(child):
                    stack.append((child, grand_child))
        return sub_g
    
    @classmethod
    def assign_vertex_weight(cls, g, ref_vect, dist_func):
        """
        Assign vertex weight by the difference between
        vertex topic vector and reference vector
        
        Return:
        -----------
        a DAG, whose nodes are weighted accordingly on attribute 'w'
        """
        for n in g.nodes():
            assert ref_vect.shape == g.node[n]['topics'].shape, \
                'Shape mismatch {} != {}'.format(ref_vect.shape, g.node[n]['topics'].shape)
            g.node[n]['w'] = dist_func(ref_vect, g.node[n]['topics'])
        return g

    @classmethod
    def round_vertex_weight(cls, g):
        """
        rounding the vertex weight to integer
        """
        for n in g.nodes():
            g.node[n]['r_w'] = int(round(g.node[n]['w']))
        return g
