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

    for metric, df in result.items():
        plt.clf()
        fig = plt.figure()
        xs = df.columns.tolist()
        for r, series in df.iterrows():
            ys = series.tolist()
            plt.plot(xs, ys, '*-')
            plt.hold(True)
        plt.xlabel(xlabel)
        plt.ylabel(metric)
        # plt.ylim([0, 1])
        plt.legend(df.index.tolist(), loc='upper left')

        fig.savefig(
            os.path.join(output_dir,
                         '{}{}.png'.format(file_prefix, metric)
                     )
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
    
