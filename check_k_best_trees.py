import ujson as json
import cPickle as pickle
import gensim

from pprint import pprint

from meta_graph_stat import MetaGraphStat
from max_cover import argmax_k_coverage
from event_summary import summary


def main():
    import argparse
    parser = argparse.ArgumentParser('check k best trees')
    parser.add_argument('--cand_trees_path', required=True)
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--people_path', required=True)
    parser.add_argument('--corpus_dict_path', required=True)
    parser.add_argument('--lda_model_path', required=True)
    parser.add_argument('--people_repr_template', type=str,
                        default="{id}")
    parser.add_argument('-k', type=int, default=10)

    args = parser.parse_args()
    pprint(vars(args))

    interactions = json.load(open(args.interactions_path))
    people_info = json.load(open(args.people_path))

    dictionary = gensim.corpora.dictionary.Dictionary.load(
        args.corpus_dict_path
    )

    lda = gensim.models.ldamodel.LdaModel.load(
        args.lda_model_path
    )

    trees = pickle.load(open(args.cand_trees_path))

    nodes_of_trees = [set(t.nodes()) for t in trees]

    selected_ids = argmax_k_coverage(nodes_of_trees, args.k)

    summary_kws = {
        'temporal_traffic': False,
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
            'top_k': 5,
            'people_repr_template': args.people_repr_template
        }
    }

    print summary([trees[id_] for id_ in selected_ids],
                  summary_kws=summary_kws,
                  tablefmt='orgtbl')


if __name__ == '__main__':
    main()
