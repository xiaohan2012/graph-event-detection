import cPickle as pkl
from max_cover import argmax_k_coverage


def detect_events(cand_trees, K):
    nodes_of_trees = [set(t.nodes()) for t in cand_trees]
    
    selected_ids = argmax_k_coverage(nodes_of_trees, K)
    
    trees = [cand_trees[id_] for id_ in selected_ids]

    return trees


def detect_events_given_path(result_path, K):
    return detect_events(pkl.load(open(result_path)), K)
