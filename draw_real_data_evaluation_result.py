import matplotlib as mpl
mpl.use('Agg')

import numpy as np 
import os
import cPickle as pkl
import matplotlib.pyplot as plt


def plot_evalution_result(results,
                          metric,
                          xlabel,
                          titles,
                          output_dir):
    """
    subplots across different dataset
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    nrows, ncols = 2, 2

    fig = plt.figure()
    for i, result in enumerate(results):
        df = result[metric]
        ax = plt.subplot(nrows, ncols, i+1)
        plt.tight_layout()
        xs = df.columns.tolist()
        for r, series in df.iterrows():
            ys = series.tolist()
            plt.plot(xs, ys, '.-')
        plt.xticks(np.arange(np.min(xs), np.max(xs)+1, 20))
        plt.xlabel(xlabel)
        if i % 2 == 0:
            plt.ylabel(metric)
        plt.title(titles[i])

    # draw legend
    ax = plt.subplot(nrows, ncols, 4)
    xs = df.columns.tolist()
    for r, series in df.iterrows():
        ys = series.tolist()
        plt.plot(xs[:1], ys[:1])
    plt.legend(df.index.tolist(), loc='center')
    ax.set_xticklabels(())
    ax.set_yticklabels(())
    ax.axis('off')
    fig.savefig(
        os.path.join(output_dir, 'fig.png')
    )


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_paths', nargs='+')
    parser.add_argument('--metric')
    parser.add_argument('--titles', nargs='+')
    parser.add_argument('--xlabel')
    parser.add_argument('--output_dir')
    
    args = parser.parse_args()
    assert len(args.titles) == len(args.result_paths)

    results = [pkl.load(open(p)) for p in args.result_paths]

    plot_evalution_result(
        results,
        args.metric,
        xlabel=args.xlabel,
        titles=args.titles,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()
