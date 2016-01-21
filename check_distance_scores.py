import gensim
import networkx as nx
from scipy.spatial.distance import cosine
from datetime import timedelta

from interactions import InteractionsUtil as IU

from util import json_load

interactions = json_load('data/enron/interactions.json')

lda_model = gensim.models.ldamodel.LdaModel.load(
    'data/enron/model-50-50.lda'
)
dictionary = gensim.corpora.dictionary.Dictionary.load(
    'data/enron/dict.pkl'
)

different_weights = [
    {'topics': 0.2,
     'bow': 0.8},
    {'topics': 1.0},
    {'bow': 1.0},
]

for weights in different_weights:
    meta_graph_kws = {
        'dist_func': cosine,
        'decompose_interactions': True,
        'preprune_secs': timedelta(weeks=4).total_seconds(),
        'apply_pagerank': False,
        'distance_weights': weights,
    }

    g = IU.get_topic_meta_graph(
        interactions,
        lda_model=lda_model,
        dictionary=dictionary,
        undirected=False,
        given_topics=False,
        **meta_graph_kws
    )
    
    print('weights:', weights)

    out_degrees = nx.out_degree(g.nodes())
    node = max(out_degrees,
               key=lambda k: out_degrees[k])
    print('Node:\nSubject: {}\nBody: {}'.format(
        g.node[node]['subject'],
        g.node[node]['body']
    ))
    top_k_nodes = sorted(g.neighbors(), key=lambda nb: g[node][nb]['c'])[:5]
    for n in top_k_nodes:
        print('Most similar neighbor:\nSubject: {}\nBody: {}'.format(
            g.node[n]['subject'],
            g.node[n]['body']
        ))
