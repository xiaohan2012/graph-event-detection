import os
import re
import nltk
import copy

import numpy as np
import networkx as nt

from datetime import datetime
from util import load_items_by_line

from meta_graph import convert_to_meta_graph

CURDIR = os.path.dirname(os.path.abspath(__file__))


class EnronUtil(object):
    """
    To create a topical meta graph, do the following:

    - get_meta_graph
    - add_topics_to_graph
    - assign_vertex_weight
    - round_vertex_weight(if necessary)
    """
    stoplist = load_items_by_line(os.path.join(CURDIR, 'lemur-stopwords.txt'))
    valid_token_regexp = re.compile('^[a-z]+$')

    @classmethod
    def decompose_interactions(cls, interactions):
        new_interactions = []
        for i in interactions:
            if len(i['recipient_ids']) > 1:
                for rec in i['recipient_ids']:
                    interaction = copy.deepcopy(i)
                    interaction['recipient_ids'] = [rec]
                    interaction['message_id'] = u'{}.{}'.format(
                        interaction['message_id'],
                        rec)
                    new_interactions.append(interaction)
            else:
                interaction = copy.deepcopy(i)
                interaction['message_id'] = unicode(i['message_id'])
                new_interactions.append(interaction)
        return new_interactions
    
    @classmethod
    def unzip_interactions(cls, interactions):
        """
        sort interactions by time and 
        convert list of interactions to
        tuple of (interaction_names, sources, targets, time_stamps)
        """
        print(interactions)
        interactions = sorted(interactions, key=lambda r: r['datetime'])
        interaction_names = [i['message_id'] for i in interactions]
        sources = [i['sender_id'] for i in interactions]
        targets = [i['recipient_ids'] for i in interactions]
        time_stamps = [i['datetime'] for i in interactions]
        return (interaction_names, sources, targets, time_stamps)

    @classmethod
    def get_meta_graph(cls, interactions):
        """
        Return the meta graph together with temporally sorted interactions
        
        Decompose interactions if necessary
        """            
        interactions = cls.decompose_interactions(interactions)
        g = convert_to_meta_graph(*cls.unzip_interactions(interactions))
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
                len(word) > 2 and len(word) < 15)
        ]

    @classmethod
    def add_topics_to_graph(cls, g, lda_model, dictionary):
        for n in g.nodes():
            doc = u'{} {}'.format(g.node[n]['subject'], g.node[n]['body'])
            print(n, doc, cls.tokenize_document(doc))
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

    @classmethod
    def assign_edge_weights(cls, g, dist_func):
        for s, t in g.edges():
            g[s][t]['w'] = dist_func(g.node[s]['topics'], g.node[t]['topics'])
        return g
        
    @classmethod
    def round_edge_weight_to_decimal_point(cls, g, decimal_point):
        denom = float(10**decimal_point)
        for s, t in g.edges():
            g[s][t]['r_w'] = int(round(g[s][t]['w'] * denom)) / denom
        return g

    @classmethod        
    def get_topic_meta_graph(cls, interactions,
                             lda_model, dictionary,
                             dist_func,
                             weight_decimal_point=1):
        g = cls.assign_edge_weights(
            cls.add_topics_to_graph(
                cls.get_meta_graph(interactions),
                lda_model, dictionary
            ),
            dist_func
        )

        if weight_decimal_point:
            return cls.round_edge_weight_to_decimal_point(g, weight_decimal_point)
        else:
            return g
