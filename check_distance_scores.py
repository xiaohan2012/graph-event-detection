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
        'distance_weights': weights,       
    }

    g = IU.get_topic_meta_graph(
        interactions,
        lda_model=lda_model,
        dictionary=dictionary,
        undirected=False,
        given_topics=False,
        decompose_interactions=False,
        dist_func=cosine,
        preprune_secs=timedelta(weeks=4).total_seconds(),
        apply_pagerank=False,
        **meta_graph_kws
    )
    
    print('weights: {}\n'.format(weights))

    out_degrees = g.out_degree(g.nodes())
    sorted_nodes = sorted(out_degrees,
                         key=lambda k: out_degrees[k],
                         reverse=True)
    print('\n'.join(map(lambda n: g.node[n]['subject'], sorted_nodes)[:10]))

    node = sorted_nodes[5]
    
    def print_message(node):
        print('Sender: {}\nTime: {}\nSubject: {}\nBody: {}\n'.format(
                g.node[node]['sender_id'],
                g.node[node]['datetime'],
                g.node[node]['subject'],
                g.node[node]['body'][:1000]
                )
              )
    print('Node')
    print_message(node)
    top_k_nodes = sorted(g.neighbors(node), key=lambda nb: g[node][nb]['c'])[:5]
    for i, n in enumerate(top_k_nodes):
        print('{}:'.format(i))
        print_message(n)
    print('*' * 100)
