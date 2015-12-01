import os
import cPickle as pickle
import gensim
import numpy as np

from meta_graph_stat import MetaGraphStat
from max_cover import argmax_k_coverage
from util import load_json_by_line

K = 5

CURDIR = os.path.dirname(os.path.abspath(__file__))

interactions = load_json_by_line('data/enron.json')
people_info = load_json_by_line('data/people.json')

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
    },
    'participants': {
        'people_info': people_info,
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
