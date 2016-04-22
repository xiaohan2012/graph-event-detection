import pandas as pd
import codecs
from util import smart_read_df


def dump_message_ids(interactions_path, output_path):
    df = smart_read_df(interactions_path)
    with codecs.open(output_path, 'w', 'utf8') as f:
        for i, r in df.iterrows():
            f.write(
                u'{}\n'.format(r['message_id'])
                )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('dump message ids')
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--output_path', required=True)

    args = parser.parse_args()
    dump_message_ids(args.interactions_path,
                     args.output_path)
    
