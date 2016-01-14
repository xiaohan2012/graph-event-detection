import os
import sys

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
                        '-p',
                        required=True
    )
    parser.add_argument('--dirname', '-d', required=True)
    parser.add_argument('--to_original_graph',
                        action='store_true',
                        default=False)
    parser.add_argument('--undirected',
                        action='store_true',
                        default=False)
    
    args = parser.parse_args()

    if args.to_original_graph and args.undirected:
        print('ERROR: to_original_graph not allowed for undirected')
        sys.exit(-1)

    run(args.candidate_tree_path,
        args.dirname,
        args.to_original_graph)
