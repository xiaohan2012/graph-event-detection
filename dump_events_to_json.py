import os

from events import detect_events_given_path
from meta_graph import convert_to_original_graph

from util import json_dump
from viz_util import to_d3_graph
from experiment_util import get_output_path


def run(candidate_tree_path,
        dirname=None,
        to_original_graph=False):

    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    output_path = get_output_path(candidate_tree_path, dirname)

    K = 5
    events = detect_events_given_path(candidate_tree_path, K)

    if to_original_graph:
        events = map(convert_to_original_graph,
                     events)

    d3_events = [to_d3_graph(e)
                 for e in events]
    json_dump(d3_events, output_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Dump events to json')
    parser.add_argument('--candidate_tree_path',
                        required=True
    )
    parser.add_argument('--dirname')
    parser.add_argument('--to_original_graph',
                        action='store_true',
                        default=False)
    args = parser.parse_args()
    run(args.candidate_tree_path,
        args.dirname,
        args.to_original_graph)
