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

with open('data/enron.json', 'r') as f:
    id2msg = {}
    for l in f:
        m = json.loads(l)
        id2msg[m['message_id']] = "{} {}".format(m['subject'], m['body'])

dictionary = gensim.corpora.dictionary.Dictionary.load(
    os.path.join(CURDIR, 'models/dictionary.pkl')
)

lda = gensim.models.ldamodel.LdaModel.load(
    os.path.join(CURDIR, 'models/model-4-50.lda')
)

trees = pickle.load(open('tmp/results.pkl'))

nodes_of_trees = [set(t.nodes()) for t in trees]

selected_ids = argmax_k_coverage(nodes_of_trees, K)


for i in selected_ids:
    t = trees[i]
    print('Tree simmary:\n{}'.format(MetaGraphStat(t).summary()))
    message_ids = [t.node[n]['message_id']
                   for n in t.nodes()]
    concated_msg = ' '.join([id2msg[mid] for mid in message_ids])
    bow = dictionary.doc2bow(EnronUtil.tokenize_document(concated_msg))
    topic_dist = lda.get_document_topics(
        bow,
        minimum_probability=0
    )
    print(topic_dist)


mat = np.zeros((K, K))

# overlapping ratio matrix
for a, i in enumerate(selected_ids):
    for b, j in enumerate(selected_ids):
        s1 = set(trees[i].nodes())
        s2 = set(trees[j].nodes())
        mat[a][b] = len(s1.intersection(s2)) / float(len(s1))

print(mat)
