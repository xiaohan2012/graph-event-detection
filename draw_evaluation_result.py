import matplotlib as mpl
mpl.use('Agg')

import numpy as np 
import os
import cPickle as pkl
import matplotlib.pyplot as plt
from matplotlib import lines
line_styles = lines.lineStyles.keys()

from global_vars import legend_mapping, mpl_font, label_mapping, markers, colors
mpl.rc('font', **mpl_font)


def plot_evalution_result(result, output_dir,
                          subplot_ordering,
                          xlabel='U',
                          file_prefix='',
                          figure_size=(None, None)):
    """
    result: similar to 3d matrix (metric, method, U)
    """
    print figure_size
    if figure_size[0] and figure_size[1]:
        print('changing size', figure_size)
        from pylab import rcParams
        rcParams['figure.figsize'] = figure_size

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    nrows, ncols = 2, 3

    fig = plt.figure()
    for i, metric in enumerate(subplot_ordering):
        df = result[metric]
        ax = plt.subplot(nrows, ncols, i+1)
        plt.tight_layout()
        xs = df.columns.tolist()
        for ith, (r, series) in enumerate(df.iterrows()):
            ys = series.tolist()
            plt.plot(xs, ys, marker=markers[ith], color=colors[ith], markersize=6, linewidth=3.0)
        plt.xticks(np.arange(np.min(xs), np.max(xs)+1, 20))
        if i / ncols > 0:
            plt.xlabel(xlabel)
        plt.ylabel(label_mapping.get(metric, metric))
        ax.yaxis.label.set_size(20)
        ax.xaxis.label.set_size(20)
        all_ys = [e for r, s in df.iterrows() for e in s.tolist()]
        if np.min(all_ys) >= 0:
            plt.ylim(ymin=0)
        plt.ylim(ymax=np.max(all_ys)+0.1)

    # draw legend
    ax = plt.subplot(nrows, ncols, 6)
    xs = df.columns.tolist()
    for ith, (r, series) in enumerate(df.iterrows()):
        ys = series.tolist()
        plt.plot(xs[:1], ys[:1],
                 marker=markers[ith], color=colors[ith])
    plt.legend(map(lambda k: legend_mapping[k], df.index.tolist()),
               loc='lower right')
    ax.set_xticklabels(())
    ax.set_yticklabels(())
    ax.axis('off')
    fig.savefig(
        os.path.join(output_dir, 'together.png'),
        bbox_inches='tight'
    )


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_path')
    parser.add_argument('--subplot_ordering', nargs='+')
    parser.add_argument('--xlabel', default='x')
    parser.add_argument('--figure_height', type=float)
    parser.add_argument('--figure_width', type=float)
    parser.add_argument('--output_dir')
    
    args = parser.parse_args()
    result = pkl.load(open(args.result_path))
    plot_evalution_result(
        result,
        xlabel=args.xlabel,
        subplot_ordering=args.subplot_ordering,
        output_dir=args.output_dir,
        figure_size=(args.figure_width, args.figure_height)
    )

if __name__ == '__main__':
    main()
    
