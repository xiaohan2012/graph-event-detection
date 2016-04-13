import os
import re
import nltk
import copy
import logging
import time

import numpy as np
import networkx as nx

from datetime import datetime as dt
from memory_profiler import profile
from scipy.sparse import csr_matrix, issparse
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from scipy.spatial.distance import cosine
from scipy.spatial.distance import jaccard

from util import load_items_by_line, get_datetime, compose, json_load
from hig import construct_hig_from_interactions
from meta_graph import convert_to_meta_graph, \
    convert_to_meta_graph_undirected

CURDIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(format="%(asctime)s;%(levelname)s;%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("InteractionsUtil")
logger.setLevel(logging.DEBUG)


class InteractionsUtil(object):
    """
    To create a topical meta graph, do the following:

    - get_meta_graph
    - add_topics_to_graph
    - assign_vertex_weight
    - round_vertex_weight(if necessary)
    """
    VERTEX_REWARD_KEY = 'r'
    EDGE_COST_KEY = 'c'
    
    stoplist = load_items_by_line(os.path.join(CURDIR, 'lemur-stopwords.txt'))
    # valid_token_regexp = re.compile('^[a-z]+$')
    valid_token_regexp = re.compile('^[a-zA-Z][a-zA-Z0-9]?[_()\-a-zA-Z0-9]+$')

    @classmethod
    def clean_interactions(self, interactions, undirected=False,
                           convert_time=True):
        """Some cleaning. Functional
        """
        new_interactions = []
        for row_n, i in enumerate(interactions):
            if row_n % 5000 == 0:
                logger.debug("cleaning: {} / {}".format(
                    row_n,
                    len(interactions))
                )

            i = copy.deepcopy(i)
            if not undirected:
                # remove duplicate recipients
                i['recipient_ids'] = list(set(i['recipient_ids']))
            else:
                i['participant_ids'] = list(set(i['participant_ids']))

            if 'timestamp' in i:
                i['datetime'] = i['timestamp']
            if convert_time:
                # normalize datetime and timestamp
                try:
                    i['datetime'] = get_datetime(i['datetime'])
                except TypeError:
                    logger.warn(
                        'Error parsing datetime, {} of type {}'.format(
                            i['datetime'],
                            type(i['datetime'])
                        )
                    )
                    continue

            new_interactions.append(i)
        return new_interactions

    @classmethod
    def decompose_interactions(cls, interactions):
        new_interactions = []
        for i in interactions:
            recs = set(i['recipient_ids'])  # remove duplicates
            if len(recs) > 1:
                new_node_name = lambda rec: u'{}.{}'.format(
                    i['message_id'],
                    rec)
                decomposed_node_names = map(new_node_name, recs)
                for rec in recs:
                    interaction = copy.deepcopy(i)
                    interaction['recipient_ids'] = [rec]

                    # the transformed message_id
                    # can be different from original
                    interaction['message_id'] = new_node_name(rec)

                    interaction['original_message_id'] = i['message_id']

                    # to avoid document vector being calculated multiple times,
                    # we add this additional attr
                    interaction['peers'] = decomposed_node_names

                    new_interactions.append(interaction)
            else:
                interaction = copy.deepcopy(i)
                interaction['message_id'] = unicode(i['message_id'])
                interaction['original_message_id'] = i['message_id']
                interaction['peers'] = []
                new_interactions.append(interaction)
        return new_interactions
    
    @classmethod
    def unzip_interactions(cls, interactions):
        """
        sort interactions by time and
        convert list of interactions to
        tuple of (interaction_names, sources, targets, datetimes)
        """
        # sorting is important
        interactions = sorted(interactions, key=lambda r: r['datetime'])
        
        interaction_names = [i['message_id'] for i in interactions]
        sources = [i['sender_id'] for i in interactions]
        targets = [i['recipient_ids'] for i in interactions]
        datetimes = [i['datetime'] for i in interactions]

        return (interaction_names, sources, targets, datetimes)

    @classmethod
    def unzip_interactions_undirected(cls, interactions):
        """
        undirected case
        tuple of (interaction_names, participants, datetimes)
        """
        # sorting is important
        interactions = sorted(interactions, key=lambda r: r['datetime'])
        
        interaction_names = [i['message_id'] for i in interactions]
        particpants = [i['participant_ids'] for i in interactions]
        datetimes = [i['datetime'] for i in interactions]

        return (interaction_names, particpants, datetimes)

    @classmethod
    def get_meta_graph(cls, interactions,
                       undirected=False,
                       preprune_secs=None,
                       decompose_interactions=True,
                       remove_singleton=True,
                       given_topics=False,
                       apply_pagerank=False,
                       convert_time=True):
        """
        Return the meta graph together with temporally sorted interactions
        
        Decompose interactions if requested
        """
        if decompose_interactions:
            if undirected:
                raise ValueError('Non-sense to deompose for undirected graph')

            logger.info("decomposing and cleaning interactions...")
            interactions = cls.decompose_interactions(
                cls.clean_interactions(
                    interactions,
                    undirected=undirected,
                    convert_time=convert_time
                )
            )
        else:
            logger.info("cleaning interactions...")
            interactions = cls.clean_interactions(
                interactions,
                undirected=undirected,
                convert_time=convert_time
            )

        if not undirected:
            logger.info('processing **directed** interactions')
            g = convert_to_meta_graph(*cls.unzip_interactions(interactions),
                                      preprune_secs=preprune_secs)
        else:
            logger.info('processing **undirected** interactions')
            g = convert_to_meta_graph_undirected(
                *cls.unzip_interactions_undirected(interactions),
                preprune_secs=preprune_secs
            )
        for i in interactions:
            n = i['message_id']
            if decompose_interactions:
                g.node[n]['message_id'] = i['original_message_id']
            else:
                g.node[n]['message_id'] = i['message_id']

            if not given_topics:
                g.node[n]['body'] = i['body']
                g.node[n]['subject'] = i['subject']
            else:
                g.node[n]['topics'] = i['topics']
                    
            g.node[n]['datetime'] = i['datetime']

            if 'hashtags' in i:
                g.node[n]['hashtags'] = i['hashtags']

            g.node[n][cls.VERTEX_REWARD_KEY] = 1

            if decompose_interactions:
                g.node[n]['peers'] = i['peers']

            if undirected:
                g.node[n]['participant_ids'] = i['participant_ids']
            else:
                g.node[n]['sender_id'] = i['sender_id']
                g.node[n]['recipient_ids'] = i['recipient_ids']
        
        if remove_singleton:
            for n in g.nodes():
                if g.degree(n) == 0:
                    g.remove_node(n)

        # override reward scores
        if apply_pagerank:
            logger.info('Appling pagerank to get node rewark')
            g = cls.add_rewards_to_nodes_using_pagerank(g, interactions)
        
        return g

    @classmethod
    def add_recency(cls, g,
                    alpha=1.0, tau=0.8,
                    timestamp_converter=lambda s: s):
        """
        substract some edge weight by the recency of the edge,
        e.g,  \alpha \tau^{t2 - t1}
        """
        raise Exception("Not in use")
        for s, t in g.edges_iter():
            t1 = timestamp_converter(g.node[s]['timestamp'])
            t2 = timestamp_converter(g.node[t]['timestamp'])
            diff_t = t2 - t1
            recency = alpha * (tau ** diff_t)
            g[s][t]['orig_c'] = g[s][t][cls.EDGE_COST_KEY]
            g[s][t]['recency'] = recency

            g[s][t][cls.EDGE_COST_KEY] -= recency
            if g[s][t][cls.EDGE_COST_KEY] < 0:
                g[s][t][cls.EDGE_COST_KEY] = 0

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
        """
        """
        N = g.number_of_nodes()
        for i, n in enumerate(g.nodes_iter()):
            if i % 1000 == 0:
                logger.debug('adding topics: {} / {}'.format(i, N))
            doc = u'{} {}'.format(g.node[n]['subject'], g.node[n]['body'])
            bow = dictionary.doc2bow(cls.tokenize_document(doc))
            topic_dist = lda_model.get_document_topics(
                bow,
                minimum_probability=0
            )
            g.node[n]['topics'] = np.asarray([v for _, v in topic_dist],
                                             dtype=np.float)
            g.node[n]['doc_bow'] = bow
            
        return g

    @classmethod
    def build_bow_matrix(cls, g, dictionary):
        logger.debug('Building BoW matrix...')
        N = g.number_of_nodes()
        row_ind = []
        col_ind = []
        data = []
        n2i = {n: i
               for i, n in enumerate(g.nodes_iter())}
        for i, n in enumerate(g.nodes_iter()):
            if i % 1000 == 0:
                logger.debug('adding BoW: {} / {}'.format(i, N))
            doc = u'{} {}'.format(g.node[n]['subject'], g.node[n]['body'])
            for word_id, cnt in dictionary.doc2bow(
                    cls.tokenize_document(doc)):
                row_ind.append(i)
                col_ind.append(word_id)
                data.append(cnt)
        return (n2i,
                csr_matrix(
                    (
                        data,
                        (row_ind, col_ind)
                    ),
                    shape=(N, len(dictionary.keys())))
            )
        
    @classmethod
    def add_hastag_bow_to_graph(cls, g):
        text = [' '.join(g.node[n]['hashtags'])
                for n in g.nodes_iter()]
        tfidf = TfidfVectorizer(preprocessor=None,
                                tokenizer=lambda s: s.split(),
                                stop_words=None)
        
        mat = tfidf.fit_transform(text)

        N = g.number_of_nodes()

        for i, n in enumerate(g.nodes_iter()):
            if i % 1000 == 0:
                logger.debug('adding hashtag BoW: {} / {}'.format(i, N))
            g.node[n]['hashtag_bow'] = mat[i, :]
        return g
    
    @classmethod
    def add_bow_to_graph(cls, g, dictionary):
        node2row, bow_mat = cls.build_bow_matrix(g, dictionary)
        
        tfidf = TfidfTransformer()
        tfidf_mat = tfidf.fit_transform(bow_mat)
        
        # build matrix
        N = g.number_of_nodes()
        for i, n in enumerate(g.nodes_iter()):
            if i % 1000 == 0:
                logger.debug('adding BoW: {} / {}'.format(i, N))
            g.node[n]['bow'] = tfidf_mat[node2row[n], :]
        return g

    @classmethod
    def add_rewards_to_nodes(cls, g, reward_func):
        for n in g.nodes_iter():
            g.node[n][cls.VERTEX_REWARD_KEY] = reward_func(n)
        return g

    @classmethod
    def add_rewards_to_nodes_using_pagerank(cls,
                                            g, interactions,
                                            pagerank_func=nx.pagerank,
                                            **pr_kwargs):
        hig = construct_hig_from_interactions(interactions)
        pr = nx.pagerank(hig, **pr_kwargs)
        reward_func = lambda n: pr.get(n, 0.0)
        return cls.add_rewards_to_nodes(g, reward_func)
        
    @classmethod
    def filter_dag_given_root(cls, g, r, filter_func):
        """filter nodes given root and some filter function

        Return:
        a DAG, sub_g of which all nodes in sub_g passes filter_func
        """
        dag = nx.DiGraph()
        stack = [(r, None)]  # current node and ancestor parent

        # prevent re-push impossible nodes
        # e.g: A, B, C -> bad_nodes
        # black_node_set = set()

        # prevent re-pushing pushed edges
        # e.g: A, B, C, -> good_node -> C, E, F
        # white_edge_set = set()

        failed_nodes = set()
        expanded_nodes = set()

        while len(stack) > 0:
            node, parent = stack.pop()
            dag.add_node(node, g.node[node])
            if parent is not None:
                dag.add_edge(parent, node, g[parent][node])

            if node not in expanded_nodes:
                for child in g.neighbors(node):
                    if child not in failed_nodes:
                        if filter_func(child):
                            stack.append((child, node))
                        else:
                            failed_nodes.add(child)
            expanded_nodes.add(node)
        return dag

    @classmethod
    def get_rooted_subgraph_within_timespan(cls, g, r, secs):
        """collect the subtrees, st, rooted at r that all nodes in st
        are within a timeframe of length secs start from r['datetime']
        """
        return cls.filter_dag_given_root(
            g, r,
            lambda n:
            ((g.node[n]['datetime'] - g.node[r]['datetime']).total_seconds() <= secs)
        )

    @classmethod
    def add_penalty_to_self_talking_edges(cls, g, penalty):
        for s, t in g.edges_iter():
            if g.node[s]['sender_id'] == g.node[t]['sender_id']:
                # print('before:', g[s][t][cls.EDGE_COST_KEY])
                g[s][t][cls.EDGE_COST_KEY] += penalty
                # print('after:', g[s][t][cls.EDGE_COST_KEY])
        return g

    @classmethod
    def assign_edge_weights(cls, g,
                            dist_func,
                            fields_with_weights={'topics': 1}):
        """
        TODO: can be parallelized
        """
        N = g.number_of_edges()
        dists_mat = np.zeros((N, len(fields_with_weights)))

        fields, fields_weight = fields_with_weights.keys(), \
                                fields_with_weights.values()
        for i, (s, t) in enumerate(g.edges_iter()):
            if i % 10000 == 0:
                logger.debug('adding edge cost: {}/{}'.format(i, N))

            for j, f in enumerate(fields):
                if issparse(g.node[s][f]):
                    array1 = np.array(g.node[s][f].todense()).ravel()
                else:
                    array1 = np.array(g.node[s][f])

                if issparse(g.node[t][f]):
                    array2 = np.array(g.node[t][f].todense()).ravel()
                else:
                    array2 = np.array(g.node[t][f])

                # at least one is all-zero
                if not array1.any() or not array2.any():
                    dists_mat[i, j] = 1
                else:
                    if f == 'hashtag_bow':
                        # special treatment to `hashtag_bow`
                        dists_mat[i, j] = jaccard(
                            array1,
                            array2
                        )
                    else:
                        dists_mat[i, j] = dist_func(
                            array1,
                            array2
                        )

                    assert not np.isinf(dists_mat[i, j])

        weight_mat = np.matrix([fields_weight]).T

        dist_mat = np.abs(np.matrix(dists_mat) * weight_mat)

        for i, (s, t) in enumerate(g.edges_iter()):
            g[s][t][cls.EDGE_COST_KEY] = dist_mat[i, 0]
            assert not np.isinf(g[s][t][cls.EDGE_COST_KEY]), \
                (g.node[s]['bow'].nonzero(),
                 g.node[t]['bow'].nonzero())
        
        return g
        
    @classmethod
    def get_topic_meta_graph_from_synthetic(cls,
                                            path,
                                            preprune_secs,
                                            **kwargs):
        return cls.get_topic_meta_graph(json_load(path),
                                        cosine,
                                        preprune_secs=preprune_secs,
                                        decompose_interactions=False,
                                        given_topics=True,
                                        convert_time=False,
                                        **kwargs
                                    )

    @classmethod
    def get_topic_meta_graph(cls, interactions,
                             dist_func,
                             lda_model=None, dictionary=None,
                             undirected=False,
                             preprune_secs=None,
                             decompose_interactions=True,
                             remove_singleton=True,
                             given_topics=False,
                             apply_pagerank=False,
                             distance_weights={'topics': 1},
                             convert_time=True,
                             # consider_recency=False,
                             # alpha=1.0, tau=0.8,
                             # timestamp_converter=lambda s: s,
                             # self_talking_penalty=0
                             ):
        logger.debug('getting meta graph...')
        mg = cls.get_meta_graph(interactions,
                                undirected=undirected,
                                decompose_interactions=decompose_interactions,
                                preprune_secs=preprune_secs,
                                remove_singleton=remove_singleton,
                                given_topics=given_topics,
                                apply_pagerank=apply_pagerank,
                                convert_time=convert_time)

        if not given_topics:
            for k in distance_weights:
                assert k in ('bow', 'topics', 'hashtag_bow')

            if 'topics' in distance_weights and distance_weights['topics'] > 0:
                logger.debug('adding topics...')
                mg = cls.add_topics_to_graph(
                    mg,
                    lda_model,
                    dictionary
                )
            if 'bow' in distance_weights and distance_weights['bow'] > 0:
                logger.debug('adding bow...')
                mg = cls.add_bow_to_graph(
                    mg,
                    dictionary
                )

            if 'hashtag_bow' in distance_weights and \
               distance_weights['hashtag_bow'] > 0:
                logger.debug('adding hashtag bow...')
                mg = cls.add_hastag_bow_to_graph(mg)
        else:
            logger.info('topics are given')
            for n in mg.nodes_iter():
                mg.node[n]['topics'] = np.array(mg.node[n]['topics'])

        logger.debug('assiging edge weights')
        g = cls.assign_edge_weights(mg,
                                    dist_func,
                                    distance_weights
                                )
        # if self_talking_penalty:
        #     logger.debug('adding self-talking penalty')
        #     g = cls.add_penalty_to_self_talking_edges(g, self_talking_penalty)

        # if consider_recency:
        #     g = cls.add_recency(g,
        #                         alpha=alpha,
        #                         tau=tau,
        #                         timestamp_converter=timestamp_converter)
        return g

    @classmethod
    def compactize_meta_graph(cls, g, map_nodes=True):
        """remove unnecessary fields and convert node name to integer
        """
        g = g.copy()
            
        # remove topics, body, subject to save space
        fields = ['subject', 'body', 'peers', 'doc_bow']
        for n in g.nodes():
            for f in fields:
                if f in g.node[n]:
                    del g.node[n][f]
        
        if map_nodes:
            # map node id to integer
            node_str2int = {n: i
                            for i, n in enumerate(g.nodes())}
            return (nx.relabel_nodes(g,
                                     mapping=node_str2int, copy=True),
                    node_str2int)
        else:
            return g
                
    @classmethod
    def preprune_edges_by_timespan(cls, g, secs):
        """for each node, prune its children nodes
        that are temporally far away from it
        """
        if isinstance(g.node[g.nodes()[0]]['datetime'], dt):
            is_datetime = True
        else:
            is_datetime = False

        g = g.copy()
        for n in g.nodes():
            nbrs = g.neighbors(n)
            for nb in nbrs:
                time_diff = (g.node[nb]['datetime'] - g.node[n]['datetime'])
                if is_datetime:
                    time_diff = time_diff.total_seconds()
                if time_diff > secs:
                    g.remove_edge(n, nb)
        return g

clean_decom_unzip = compose(
    InteractionsUtil.clean_interactions,
    InteractionsUtil.decompose_interactions,
    InteractionsUtil.unzip_interactions
)

clean_unzip = compose(
    InteractionsUtil.clean_interactions,
    InteractionsUtil.unzip_interactions
)
