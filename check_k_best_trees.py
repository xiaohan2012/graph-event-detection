import cPickle as pickle
from pprint import pprint

from max_cover import argmax_k_coverage
from event_summary import summary
from meta_graph_stat import build_default_summary_kws_from_path


def k_best_trees(cand_trees, k):
    print('removing self-talking event')
    print('before, len(cand_trees):', len(cand_trees))
    # cand_trees = [t for t in cand_trees
    #               if len(set(t.node[n]['sender_id']
    #                          for n in t.nodes_iter())) > 1]
    # print('after, len(cand_trees):', len(cand_trees))

    nodes_of_trees = [set(t.nodes()) for t in cand_trees]

    selected_ids = argmax_k_coverage(nodes_of_trees, k)
    
    return [cand_trees[id_] for id_ in selected_ids]


def get_k_best_tree_summary(
        interactions_path, people_path,
        corpus_dict_path, lda_model_path,
        cand_trees_path, k, people_repr_template,
        undirected=False):

    summary_kws = build_default_summary_kws_from_path(
        interactions_path, people_path,
        corpus_dict_path, lda_model_path,
        people_repr_template, undirected=undirected
    )

    trees = k_best_trees(pickle.load(open(cand_trees_path)),
                         k)

    return summary(trees,
                   summary_kws=summary_kws,
                   tablefmt='orgtbl')


def main():
    import argparse
    parser = argparse.ArgumentParser('check k best cand_trees')
    parser.add_argument('--cand_trees_path', required=True)
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--people_path', required=True)
    parser.add_argument('--corpus_dict_path', required=True)
    parser.add_argument('--lda_model_path', required=True)
    parser.add_argument('--people_repr_template', type=str,
                        default="{id}")
    parser.add_argument('-k', type=int, default=10)
    parser.add_argument('--undirected', default=False, action="store_true")

    args = parser.parse_args()
    pprint(vars(args))
    print(get_k_best_tree_summary(**vars(args)))

if __name__ == '__main__':
    main()
