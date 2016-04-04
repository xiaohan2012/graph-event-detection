import matplotlib as mpl
mpl.use('Agg')

import numpy as np 
import os
import cPickle as pkl
import matplotlib.pyplot as plt

from global_vars import legend_mapping, mpl_font, label_mapping, ban_list, markers, colors
# mpl_font['size']=18


def plot_evalution_result(results,
                          metric,
                          xlabel,
                          titles,
                          output_path,
                          legend_in_which_subplot=1,
                          layout=(2, 2),
                          figure_size=(None, None)):
    """
    subplots across different dataset
    """
    font_size = 22
    legend_fontsize = 18
    if figure_size[0] and figure_size[1]:
        from pylab import rcParams
        rcParams['figure.figsize'] = figure_size

    output_dir=os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    nrows, ncols = layout

    fig = plt.figure()
    for i, result in enumerate(results):
        df = result[metric]
        ax = plt.subplot(nrows, ncols, i+1)
        plt.tight_layout()
        xs = df.columns.tolist()
        for ith, (r, series) in enumerate(df.iterrows()):
            if r not in ban_list:
                ys = series.tolist()
                plt.plot(xs, ys, marker=markers[ith], color=colors[ith], markersize=10, linewidth=3.0)
        plt.xticks(np.arange(np.min(xs), np.max(xs)+1, 20))
        plt.xlabel(xlabel)
        ax.yaxis.label.set_size(font_size)
        ax.xaxis.label.set_size(font_size)
        if i % ncols == 0:
            plt.ylabel(label_mapping.get(metric, metric))
        plt.title(titles[i], fontsize=font_size)

        legends = [a for a in df.index.tolist() if a not in ban_list]
        if i+1 == legend_in_which_subplot:
            mpl.rc('font', size=legend_fontsize)
            plt.legend(map(lambda k: legend_mapping.get(k, k), legends),
                       loc='lower right')

    fig.savefig(output_path)


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_paths', nargs='+')
    parser.add_argument('--metric')
    parser.add_argument('--titles', nargs='+')
    parser.add_argument('--xlabel')
    parser.add_argument('--legend_in_which_subplot', type=int)
    parser.add_argument('--ncols', type=int, default=2)
    parser.add_argument('--nrows', type=int, default=2)
    parser.add_argument('--figure_height', type=int)
    parser.add_argument('--figure_width', type=int)
    parser.add_argument('--output_path')
    
    args = parser.parse_args()
    assert len(args.titles) == len(args.result_paths)

    results = [pkl.load(open(p)) for p in args.result_paths]

    plot_evalution_result(
        results,
        args.metric,
        xlabel=args.xlabel,
        titles=args.titles,
        output_path=args.output_path,
        legend_in_which_subplot=args.legend_in_which_subplot,
        layout=(args.nrows, args.ncols),
        figure_size=(args.figure_width, args.figure_height)
    )

if __name__ == '__main__':
    main()
