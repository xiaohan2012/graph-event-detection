import codecs
from util import json_load


def dump_lines_of_message(interactions_path, output_path):
    obj = json_load(interactions_path)
    with codecs.open(output_path, 'w', 'utf8') as f:
        for r in obj:
            f.write(u'{} {}\n'.format(
                r['subject'].replace('\n', ' '),
                r['body'].replace('\n', ' ')))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('dump_lines_of_message')
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--output_path', required=True)

    args = parser.parse_args()
    dump_lines_of_message(args.interactions_path, args.output_path)

