import cPickle as pkl
import pandas as pd
import numpy as np


def combine(results):
    """
    ronuds of experiment result
    results: list<dict<str, pandas.DataFrame>>
    """
    metrics = results[0].keys()
    
    combined_result = {}
    # reduce
    for m in metrics:
        acc = np.zeros(results[0][m].as_matrix().shape)
        columns = results[0][m].columns
        index = results[0][m].index

        data3d = []
        for r in results:
            mat = r[m].as_matrix()
            # if mat.shape == (5, 41):
            #     print "debug!! if you see it, please think if you should remove it"
            print mat.shape
            data3d.append(mat)
        # print(data3d)
        mean_val = np.nanmean(np.asarray(data3d), axis=0)
        combined_result[m] = pd.DataFrame(
            mean_val,
            columns=columns,
            index=index
        )
    return combined_result


def main():
    import argparse

    parser = argparse.ArgumentParser('')
    parser.add_argument('--result_paths',
                        nargs='+')
    parser.add_argument('--output_path',
                        required=True)
    args = parser.parse_args()

    results = [pkl.load(open(p)) for p in args.result_paths]

    pkl.dump(combine(results),
             open(args.output_path, 'w'))


if __name__ == '__main__':
    main()
