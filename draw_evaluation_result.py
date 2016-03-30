import matplotlib as mpl
mpl.use('Agg')

import numpy as np 
import os
import cPickle as pkl
import matplotlib.pyplot as plt


def plot_evalution_result(result, output_dir,
                          subplot_ordering,
                          xlabel='U',
                          file_prefix=''):
    """
    result: similar to 3d matrix (metric, method, U)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    nrows, ncols = 2, 3

    fig = plt.figure()
    for i, metric in enumerate(subplot_ordering):
        df = result[metric]
        plt.subplot(nrows, ncols, i+1)
        plt.tight_layout()
        xs = df.columns.tolist()
        for r, series in df.iterrows():
            ys = series.tolist()
            plt.plot(xs, ys, '.-')
        plt.xticks(np.arange(np.min(xs), np.max(xs)+1, 20))
        plt.xlabel(xlabel)
        plt.ylabel(metric)

    # draw legend
    ax = plt.subplot(nrows, ncols, 6)
    xs = df.columns.tolist()
    for r, series in df.iterrows():
        ys = series.tolist()
        plt.plot(xs[:1], ys[:1])
    plt.legend(df.index.tolist(), loc='lower right')
    ax.set_xticklabels(())
    ax.set_yticklabels(())
    ax.axis('off')
    fig.savefig(
        os.path.join(output_dir, 'together.png')
    )


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_path')
    parser.add_argument('--subplot_ordering', nargs='+')
    parser.add_argument('--xlabel', default='x')
    parser.add_argument('--output_dir')
    
    args = parser.parse_args()
    result = pkl.load(open(args.result_path))
    plot_evalution_result(
        result,
        xlabel=args.xlabel,
        subplot_ordering=args.subplot_ordering,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()
    
