import matplotlib as mpl
mpl.use('Agg')

import os
import cPickle as pkl
import matplotlib.pyplot as plt


def plot_evalution_result(result, output_dir,
                          xlabel='U',
                          file_prefix=''):
    """
    result: similar to 3d matrix (metric, method, U)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.clf()
    nrows, ncols = 2, 5

    fig = plt.figure()

    for i, (metric, df) in enumerate(result.items()):
        plt.subplot(nrows, ncols, i+1)
        xs = df.columns.tolist()
        for r, series in df.iterrows():
            ys = series.tolist()
            plt.plot(xs, ys)

        plt.xlabel(xlabel)
        plt.ylabel(metric)
        plt.title(metric)
    fig.legend(df.index.tolist(), loc='lower right')

    fig.savefig(
        os.path.join(output_dir, 'together.png')
    )


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_path')
    parser.add_argument('--xlabel', default='x')
    parser.add_argument('--output_dir')
    
    args = parser.parse_args()
    result = pkl.load(open(args.result_path))
    plot_evalution_result(
        result,
        xlabel=args.xlabel,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()
    
