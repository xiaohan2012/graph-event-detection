import matplotlib as mpl
mpl.use('Agg')

import os
import matplotlib.pyplot as plt
import itertools
import cPickle as pkl
import pandas as pd
import numpy as np

from glob import glob
from sklearn import metrics

from util import json_load
from experiment_util import parse_result_path
from max_cover import k_best_trees
from evaluation import evaluate_meta_tree_result


def group_paths(paths, keyfunc, sort_keyfunc=None):
    """
    key: lambda
    
    return :flattened array
    """
    exp_params = [(p, parse_result_path(p))
                  for p in paths]
    ret = []
    key = lambda (_, params): keyfunc(params)
    exp_params = sorted(exp_params, key=key)  # sort them
    for k, g in itertools.groupby(
            exp_params, key):
        if sort_keyfunc is None:
            sorted_g = sorted(list(g))
        else:
            sorted_g = sorted(list(g),
                              key=lambda (p, param):
                              sort_keyfunc(param))
        ret.append((k, [p for p, _ in sorted_g]))
    return ret


def get_values_by_key(paths, key, map_func):
    return [map_func(parse_result_path(p)[key])
            for p in paths]


def evaluate_general(
        paths, interactions_path, events_path, metrics,
        x_axis_name, x_axis_type,
        group_key, group_key_name_func,
        K=10):
    interactions = json_load(interactions_path)
    all_entry_ids = [i['message_id'] for i in interactions]
    true_events = json_load(events_path)
    
    groups = group_paths(paths, group_key)
    xs = sorted(
        get_values_by_key(groups[0][1],
                          x_axis_name,
                          x_axis_type)
    )
    group_keys = [k for k, _ in groups]
    metric_names = evaluate_meta_tree_result(
        true_events,
        k_best_trees(
            pkl.load(open(groups[0][1][0])), K
        ),
        all_entry_ids,
        metrics
    ).keys()  # extra computing

    # 3d array: (method, U, metric)
    data3d = np.array([
        [evaluate_meta_tree_result(
            true_events,
            k_best_trees(pkl.load(open(p)), K),
            all_entry_ids,
            metrics).values()
         for p in sub_paths]
        for key, sub_paths in groups])

    # change axis to to (metric, method, U)
    data3d = np.swapaxes(data3d, 0, 1)
    data3d = np.swapaxes(data3d, 0, 2)

    group_keys = [group_key_name_func(k)
                  for k in group_keys]
    ret = {}
    for metric, matrix in itertools.izip(metric_names, data3d):
        ret[metric] = pd.DataFrame(matrix, columns=xs, index=group_keys)

    return ret


def evaluate_U(paths, interactions_path, events_path, metrics,
               K=10):
    return evaluate_general(
        paths, interactions_path, events_path, metrics,
        x_axis_name='U', x_axis_type=float,
        group_key=lambda p: (p['args'][0], p['dijkstra']),
        group_key_name_func=(lambda (m, dij):
                             ("{}-dij".format(m)
                              if dij == 'True' else m)),
        K=K
    )


def evaluate_preprune_seconds(paths, interactions_path,
                              events_path, metrics,
                              K=10):
    return evaluate_general(
        paths, interactions_path, events_path, metrics,
        x_axis_name='preprune_secs', x_axis_type=int,
        group_key=lambda p: 'greedy',
        group_key_name_func=lambda k: k,
        K=10
    )


def evaluate_sampling(paths, interactions_path,
                      events_path, metrics,
                      K=10):
    return evaluate_general(
        paths, interactions_path, events_path, metrics,
        x_axis_name='cand_tree_percent', x_axis_type=float,
        group_key=lambda p: p['root_sampling'],
        group_key_name_func=lambda k: k,
        K=10
    )


def plot_evalution_result(result, output_dir, file_prefix=''):
    """
    result: similar to 3d matrix (metric, method, U)
    """
    for metric, df in result.items():
        plt.clf()
        fig = plt.figure()
        xs = df.columns.tolist()
        for r, series in df.iterrows():
            ys = series.tolist()
            plt.plot(xs, ys, '*-')
            plt.hold(True)
        plt.xlabel('U')
        plt.ylabel('method')
        plt.ylim([0, 1])
        plt.legend(df.index.tolist(), loc='upper left')

        fig.savefig(
            os.path.join(output_dir,
                         '{}{}.png'.format(file_prefix, metric)
                     )
        )


def main(exp_name):
    exp_func = {
        'preprune_seconds': evaluate_preprune_seconds,
        'U': evaluate_U,
        'sampling': evaluate_sampling
    }
    func = exp_func[exp_name]
    result = func(
        paths=glob('tmp/synthetic/{}/result-*.pkl'.format(exp_name)),
        interactions_path='data/synthetic/interactions.json',
        events_path='data/synthetic/events.json',
        metrics=[metrics.adjusted_rand_score,
                 metrics.adjusted_mutual_info_score,
                 metrics.homogeneity_score,
                 metrics.completeness_score,
                 metrics.v_measure_score],
        K=10)
    plot_evalution_result(
        result,
        output_dir='/cs/home/hxiao/public_html/figures/synthetic/{}'.format(
            exp_name
        )
    )
if __name__ == '__main__':
    # main('preprune_seconds')
    main('sampling')
