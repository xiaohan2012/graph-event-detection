import matplotlib as mpl
mpl.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

from check_k_best_trees import k_best_trees


def correct_roots_ratio(acc_trees, true_trees):
    pass


def k_max_setcover(acc_trees, true_trees, k):
    acc_trees = filter(None, acc_trees)
    trees = k_best_trees(acc_trees, k)
    return len(set([n for t in trees for n in t.nodes_iter()]))


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
    parser.add_argument('--result_paths',
                        nargs='+')
    parser.add_argument('--legends',
                        nargs='+')
    parser.add_argument('--true_trees_path')
    parser.add_argument('--output_path')
    parser.add_argument('--metric',
                        default='setcover')
    parser.add_argument('-k', type=int)

    args = parser.parse_args()
    assert len(args.result_paths) == len(args.legends)
    result = {}
    
    metric_map = {
        'setcover': k_max_setcover,
    }
    metric = metric_map[args.metric]
    event_trees = pkl.load(open(args.true_trees_path))
    for result_path, legend in zip(args.result_paths, args.legends):
        result[legend] = evaluate(pkl.load(open(result_path)),
                                  event_trees,
                                  metric,
                                  k=args.k)

    fig = plt.figure()
    for ys in result.values():
        plt.plot(np.arange(len(ys)), ys)
        plt.hold(True)
    plt.xlabel('#epoch')
    plt.ylabel('obj of max k-setcover')
    plt.legend(result.keys(), loc='lower right')

    fig.savefig(args.output_path)

    
if __name__ == '__main__':
    main()
