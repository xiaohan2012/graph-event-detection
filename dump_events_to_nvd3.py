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
    parser.add_argument('--freq')
    parser.add_argument('--k', type=int)

    args = parser.parse_args()
    result = pkl.load(open(args.result_path))
    trees = k_best_trees(result, args.k)
    df = pd.read_json(args.interactions_path)

    # for enron:
    df = df[df['datetime'] > dt(2000, 6, 1)]
    
    timestamps = df.groupby(pd.Grouper(key='datetime', freq=args.freq))['message_id'].count().index
    
    values = lambda counts: [{'ts': ts.value/1000000,
                              'c': counts[ts] if ts in counts else 0}
                             for ts in timestamps]
    data = []
    event_nodes = set()
    for i, t in enumerate(trees):
        nids = set(t.nodes())
        event_df = df[df['message_id'].apply(lambda m: m in nids)]
        groups = event_df.groupby(pd.Grouper(key='datetime', freq=args.freq))
        counts = groups['message_id'].count()
        
        data.append({
            'key': 'event-{}'.format(i+1),
            'values': values(counts)
        })

        event_nodes |= nids

    df = df[df['message_id'].map(lambda m: m not in event_nodes)]

    if args.non_event_sample_n:
        df = df.sample(n=args.non_event_sample_n)

    counts = df.groupby(pd.Grouper(key='datetime', freq=args.freq))['message_id'].count()
    data.append({
        'key': 'non-event',
        'values': values(counts)
    })
    # print(data)
    json.dump(data, open(args.output_path, 'w'))

if __name__ == '__main__':
    main()
