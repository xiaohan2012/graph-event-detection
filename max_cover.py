# Algorithm for maximum coverage problem
import numpy as np


def maximum_k_coverage(sets, k):
    covered = set()
    selected_sets = []
    if k >= len(sets):
        return sets
        
    for i in xrange(k):
        max_set = max(sets, key=lambda s: len(s - covered))
        selected_sets.append(max_set)
        covered |= max_set
    return selected_sets


def argmax_k_coverage(sets, k):
    """return the indices of the selected sets
    """
    covered = set()
    selected_set_indices = []
    if k >= len(sets):
        return range(len(sets))
        
    for i in xrange(k):
        uncovered_sizes = map(lambda s: len(s - covered), sets)
        max_set_index = np.argmax(uncovered_sizes)
        selected_set_indices.append(max_set_index)
        covered |= sets[max_set_index]
    return selected_set_indices


def k_best_trees(cand_trees, K):
    nodes_of_trees = [set(t.nodes()) for t in cand_trees]
    selected_ids = argmax_k_coverage(nodes_of_trees, K)
    pred_trees = [cand_trees[i] for i in selected_ids]
    return pred_trees
