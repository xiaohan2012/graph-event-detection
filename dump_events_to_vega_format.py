import cPickle as pkl
import pandas as pd
import ujson as json

from datetime import datetime as dt
from check_k_best_trees import k_best_trees


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--result_path')
    parser.add_argument('--interactions_path')
    parser.add_argument('--output_path')
    parser.add_argument('--non_event_sample_n', type=int)
    parser.add_argument('--k', type=int)

    args = parser.parse_args()
    result = pkl.load(open(args.result_path))
    trees = k_best_trees(result, args.k)
    df = pd.read_json(args.interactions_path)
    
    dt_format = '%Y-%m-%dT%H:%M:%S.000Z'

    data = []
    event_nodes = set()
    for i, t in enumerate(trees):
        for n in t.nodes_iter():
            event_nodes.add(n)
            # print(t.node[n]['datetime'])
            data.append(
                {
                    'series': 'event-{}'.format(i+1),
                    'datetime': t.node[n]['datetime'].strftime(dt_format)
                }
            )
    # for enron:
    df = df[df['datetime'] > dt(2000, 6, 1)]

    # for ukraine:
    # df = df[df['datetime'] > dt(2015, 2, 26)]

    # for baltimore
    # df = df[df['datetime'] >= dt(2015, 4, 27)]

    if args.non_event_sample_n:
        print df.shape
        df = df[df['message_id'].map(lambda m: m not in event_nodes)]

        df = df.sample(n=args.non_event_sample_n)
        print df.shape

    for i, r in df.iterrows():
        # print(r)
        # print(r['datetime'])
        if r['message_id'] not in event_nodes:
            data.append(
                {
                    'series': 'non-event',
                    'datetime': r['datetime'].strftime(dt_format)
                }
            )
        else:
            # print "drop"
            pass

    json.dump(data, open(args.output_path, 'w'))

if __name__ == '__main__':
    main()
