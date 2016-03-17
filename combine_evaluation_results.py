import cPickle as pkl
import pandas as pd
import numpy as np


def combine(results):
    """
    results: list<dict<str, pandas.DataFrame>>
    """
    metrics = results[0].keys()
    
    combined_result = {}
    # reduce
    for m in metrics:
        acc = np.zeros(results[0][m].as_matrix().shape)
        columns = results[0][m].columns
        index = results[0][m].index

        for r in results:
            acc += r[m].as_matrix()
        
        combined_result[m] = pd.DataFrame(
            acc / len(results),
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
