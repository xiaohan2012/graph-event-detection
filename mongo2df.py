import os
import pandas as pd
from pymongo import MongoClient

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', required=True)
    parser.add_argument('-c', '--collection', required=True)
    parser.add_argument('-o', '--output_dir', required=True)

    args = parser.parse_args()

    db = MongoClient()[args.database]

    data = []
    for r in db[args.collection].find():
        del r['_id']
        r['subject'] = ''
        data.append(r)
    df = pd.DataFrame(data)

    df.to_pickle(
        os.path.join(args.output_dir,
                     'interactions.pkl')
        )

    peoples = set()
    for i, r in df.iterrows():
        peoples.add(r['sender_id'])
        for id_ in r['recipient_ids']:
            peoples.add(id_)

    people_df = pd.DataFrame.from_dict(
        {'id': list(peoples)},
        )
    people_df.to_pickle(
        os.path.join(
            args.output_dir,
            'people.pkl'
            )
        )
