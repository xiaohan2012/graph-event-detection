import os
import ujson as json
import codecs

from events import detect_events_given_path
from util import to_d3_graph


def run(candidate_tree_path, dirname=None):
    output_name = '{}.json'.format(
        ''.join(os.path.basename(candidate_tree_path).split('.')[:-1])
    )
    if dirname:
        output_path = os.path.join(dirname, output_name)
    else:
        output_path = os.path.join(os.path.dirname(candidate_tree_path),
                                   output_name)

    K = 5
    events = detect_events_given_path(candidate_tree_path, K)
    d3_events = [to_d3_graph(e)
                 for e in events]
    with codecs.open(output_path, 'w', 'utf8') as f:
        f.write(json.dumps(d3_events))

if __name__ == '__main__':
    import sys
    run(sys.argv[1], sys.argv[2])
