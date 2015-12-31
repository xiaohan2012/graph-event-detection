import os
import cPickle as pickle
import gensim
import numpy as np
import ujson as json

from meta_graph_stat import MetaGraphStat
from max_cover import argmax_k_coverage
from util import load_json_by_line
from event_summary import summary

import sys

result_path = sys.argv[1]
interactions_path = sys.argv[2]
people_path = sys.argv[3]
dictionary_path = sys.argv[4]
lda_path = sys.argv[5]

K = 10

CURDIR = os.path.dirname(os.path.abspath(__file__))

print("loading interactions...")
try:
    interactions = json.load(
        open(os.path.join(CURDIR, interactions_path))
        )
except ValueError:
    interactions = load_json_by_line(
        os.path.join(CURDIR, interactions_path)
        )

print("loading people...")
people_info = load_json_by_line(
    os.path.join(CURDIR, people_path)
    )

print("loading dict...")
dictionary = gensim.corpora.dictionary.Dictionary.load(
    os.path.join(CURDIR, dictionary_path)
)

print("loading lda...")
lda = gensim.models.ldamodel.LdaModel.load(
    os.path.join(CURDIR, lda_path)
)

print("loading candidates...")
trees = pickle.load(open(result_path))

nodes_of_trees = [set(t.nodes()) for t in trees]

print("k-max-set running...")
selected_ids = argmax_k_coverage(nodes_of_trees, K)

print("Summary:\n\n")
print summary([trees[id_] for id_ in selected_ids], 
              interactions, people_info, dictionary, lda,
              tablefmt='orgtbl')
