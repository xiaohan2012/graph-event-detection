from itertools import chain


def precision_recall_f1(true_clusters, pred_clusters):
    true_entries = set(chain(*true_clusters))
    pred_entries = set(chain(*pred_clusters))
    intersect = true_entries.intersection(pred_entries)
    p, r, = float(len(intersect)) / len(pred_entries), \
            float(len(intersect)) / len(true_entries)
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
        true_clusters, pred_clusters, all_entry_ids, metric, true_only=True):
    """
    pred_clusters, true_clusters: array of list[int]
    all_entry_ids: list[int]
    """
    true_labels, pred_labels = convert_to_cluster_assignment_array(
        true_clusters, pred_clusters, all_entry_ids,
        true_only
    )
    return metric(true_labels, pred_labels)
    

def evaluate_meta_tree_result(
        true_events, pred_trees, all_entry_ids, metric, true_only=True):
    true_clusters = [[i['message_id'] for i in e]for e in true_events]
    pred_clusters = [t.nodes() for t in pred_trees]
    
    return evaluate_clustering_result(true_clusters, pred_clusters,
                                      all_entry_ids,
                                      metric,
                                      true_only)
