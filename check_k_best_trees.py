import os
import cPickle as pickle
import ujson as json
import gensim
import numpy as np

from enron_graph import EnronUtil
from meta_graph_stat import MetaGraphStat
from max_cover import argmax_k_coverage


K = 10

CURDIR = os.path.dirname(os.path.abspath(__file__))

interactions = []
with open('data/enron.json', 'r') as f:
    for l in f:
        interactions.append(json.loads(l))

# interactions = EnronUtil.decompose_interactions(interactions)
print map(lambda m: m['message_id'], interactions)

dictionary = gensim.corpora.dictionary.Dictionary.load(
    os.path.join(CURDIR, 'models/dictionary.pkl')
)

lda = gensim.models.ldamodel.LdaModel.load(
    os.path.join(CURDIR, 'models/model-4-50.lda')
)

trees = pickle.load(open('tmp/results.pkl'))

nodes_of_trees = [set(t.nodes()) for t in trees]

selected_ids = argmax_k_coverage(nodes_of_trees, K)

STAT_KWS = {
    'temporal_traffic': {
        'time_resolution': 'day'
    },
    'topics': {
        'interactions': interactions,
        'dictionary': dictionary,
        'lda': lda,
        'top_k': 10
    },
    'email_content': {
        'interactions': interactions,
        'top_k': 5
    }
}


def get_summary(g):
    return MetaGraphStat(g, kws=STAT_KWS).summary()


for i in selected_ids:
    t = trees[i]
    print('Tree simmary:\n{}'.format(get_summary(t)))

mat = np.zeros((K, K))

# overlapping ratio matrix
for a, i in enumerate(selected_ids):
    for b, j in enumerate(selected_ids):
        s1 = set(trees[i].nodes())
        s2 = set(trees[j].nodes())
        mat[a][b] = len(s1.intersection(s2)) / float(len(s1))

print(mat)
