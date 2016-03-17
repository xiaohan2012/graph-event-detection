import sys
import numpy as np
from itertools import chain
from sklearn import metrics

from tree_util import salzburg_ted, tree_similarity_ratio


def precision_recall_f1(true_clusters, pred_clusters):
    true_entries = set(chain(*true_clusters))
    pred_entries = set(chain(*pred_clusters))
    intersect = true_entries.intersection(pred_entries)
    if len(pred_entries) == 0:
        sys.stderr.write("len(pred_entries) is 0")
        p = 0
    else:
        p = float(len(intersect)) / len(pred_entries)
    r = float(len(intersect)) / len(true_entries)
    f1 = 2 * p * r / (p + r)
    return p, r, f1


def convert_to_cluster_assignment_array(
        true_clusters, pred_clusters, all_entry_ids, true_only=True):
    true_id2label = {}
    for i, clst in enumerate(true_clusters):
        true_id2label.update({elem: i+1
                              for elem in clst})
    pred_id2label = {}
    for i, clst in enumerate(pred_clusters):
        pred_id2label.update({elem: i+1
                              for elem in clst})
    if true_only:
        true_ids = sorted(chain(*true_clusters))
        true_labels = map(lambda i: true_id2label[i],
                          true_ids)
        pred_labels = map(lambda i: pred_id2label.get(i, 0),
                          true_ids)
    else:
        all_entry_ids = sorted(all_entry_ids)
        true_labels = map(lambda i: true_id2label.get(i, 0),
                          all_entry_ids)
        pred_labels = map(lambda i: pred_id2label.get(i, 0),
                          all_entry_ids)
    return true_labels, pred_labels


def evaluate_clustering_result(
        true_clusters, pred_clusters,
        all_entry_ids,
        metric, true_only=True):
    """
    pred_clusters, true_clusters: array of list[int]
    all_entry_ids: list[int]
    """
    true_labels, pred_labels = convert_to_cluster_assignment_array(
        true_clusters, pred_clusters, all_entry_ids,
        true_only
    )
    return metric(true_labels, pred_labels)
    

def events2clusters(events):
    return [[i['message_id'] for i in e]for e in events]


def trees2clusters(trees):
    return [t.nodes() for t in trees]


def evaluate_meta_tree_result(
        true_events, pred_events, all_entry_ids, methods):
    setcover_obj = len(set([n for t in pred_events for n in t.nodes_iter()]))
    scores = {
        'set_cover_obj': setcover_obj
    }
    
    true_clusters = trees2clusters(true_events)
    pred_clusters = trees2clusters(pred_events)
    
    for m in methods:
        for true_only in (True, False):
            name = m.__name__
            if not true_only:
                name += "(all)"
            scores[name] = evaluate_clustering_result(
                true_clusters, pred_clusters,
                all_entry_ids,
                m,
                true_only)
    p, r, f1 = precision_recall_f1(true_clusters, pred_clusters)

    scores['precision'] = p
    scores['recall'] = r
    scores['f1'] = f1
    
    # mean of tree edit distance across all (true, pred) pairs
    # weighted mean can be added
    scores['tree_similarity'] = np.mean(
        [tree_similarity_ratio(
            salzburg_ted(true, pred),
            true, pred
        )
        for true, pred in zip(true_events, pred_events)]
    )
    return scores


def main():
    import os
    import cPickle as pkl
    import pandas as pd
    from util import json_load
    from max_cover import k_best_trees
    import argparse
    
    parser = argparse.ArgumentParser('Evaluate the events')
    parser.add_argument('-c', '--cand_trees_path', required=True, nargs='+')
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--events_path', required=True)
    args = parser.parse_args()

    interactions = json_load(args.interactions_path)
    true_events = json_load(args.events_path)
    methods = [metrics.adjusted_rand_score,
               metrics.adjusted_mutual_info_score,
               metrics.homogeneity_score,
               metrics.completeness_score,
               metrics.v_measure_score]

    K = 10
    indexes = []
    scores = []
    for p in args.cand_trees_path:
        cand_trees = pkl.load(open(p))
        pred_trees = k_best_trees(cand_trees, K)

        indexes.append(os.path.basename(p))
        scores.append(evaluate_meta_tree_result(
            true_events,
            pred_trees,
            [i['message_id'] for i in interactions],
            methods
        ))
    df = pd.DataFrame(scores, index=indexes,
                      columns=[m.__name__ for m in methods] +
                      [m.__name__ + "(all)" for m in methods] +
                      ['precision', 'recall', 'f1'])
    df.to_csv('tmp/evaluation.csv')

if __name__ == '__main__':
    main()
