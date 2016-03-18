import matplotlib as mpl
mpl.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

from check_k_best_trees import k_best_trees


def correct_roots_ratio(acc_trees, true_trees):
    pass


def k_max_setcover(acc_trees, true_trees, k):
    trees = k_best_trees(acc_trees, k)
    return len(set([n for t in trees for n in t.nodes_iter()]))


def get_meta_data_of_f1(acc_trees, true_trees, k):
    pred_trees = k_best_trees(acc_trees, k)
    pred_nodes = set([n for t in pred_trees for n in t.nodes_iter()])
    true_nodes = set([n for t in true_trees for n in t.nodes_iter()])
    correct_nodes = pred_nodes & true_nodes
    return float(len(correct_nodes)), len(pred_nodes), len(true_nodes)


def precision(acc_trees, true_trees, k):
    # sure, some computation waste
    c, p, _ = get_meta_data_of_f1(acc_trees, true_trees, k)
    return c / p


def recall(acc_trees, true_trees, k):
    c, _, t = get_meta_data_of_f1(acc_trees, true_trees, k)
    return c / t


def f1(acc_trees, true_trees, k):
    prec = precision(acc_trees, true_trees, k)
    rec =  recall(acc_trees, true_trees, k)
    return 2 * prec * rec / (prec + rec)


def evaluate(pred_trees, true_trees, metric, *args, **kwargs):
    scores = []
    for i in xrange(len(pred_trees)):
        acc_trees = pred_trees[:i+1]
        # if the current tree is None, repeat the score from last iteration
        if pred_trees[i] is None:
            scores.append(scores[-1])
        else:
            scores.append(
                metric(acc_trees, true_trees, *args, **kwargs)
            )
    return scores


def main():
    import cPickle as pkl
    import argparse

    parser = argparse.ArgumentParser('draw the sampler evaluation result')
    parser.add_argument('--experiment_paths',
                        nargs='+')
    parser.add_argument('--legends',
                        nargs='+')
    parser.add_argument('--output_dir')
    parser.add_argument('--metrics',
                        nargs="+")
    parser.add_argument('-k', type=int)

    args = parser.parse_args()
    assert len(args.experiment_paths) == len(args.legends), '{} != {}'.format(len(args.experiment_paths),
                                                                              len(args.legends))
    result = {}
    
    metric_map = {
        'k_setcover_obj': k_max_setcover,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

    for metric_name in args.metrics:
        metric = metric_map[metric_name]
        for experiment_path, legend in zip(sorted(args.experiment_paths),
                                           sorted(args.legends)):
            paths = pkl.load(open(experiment_path))
            result_path = paths['result']
            true_events_path = paths['true_events']

            assert legend in result_path, (legend, result_path)
            # print('result_path:', result_path)
            # print('legend:', legend)

            result[legend] = evaluate(pkl.load(open(result_path)),
                                      pkl.load(open(true_events_path)),
                                      metric,
                                      k=args.k)

        fig = plt.figure()
        fig.clf()
        for ys in result.values():
            plt.plot(np.arange(len(ys)), ys)
            plt.hold(True)
            plt.xlabel('#epoch')
            plt.ylabel(metric_name)
        plt.legend(result.keys(), loc='lower right')

        fig.savefig('{}/{}.png'.format(args.output_dir,
                                       metric_name))

    
if __name__ == '__main__':
    main()
