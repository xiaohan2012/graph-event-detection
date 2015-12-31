from events import detect_events_given_path

from util import json_dump
from viz_util import to_d3_graph
from experiment_util import get_output_path


def run(candidate_tree_path, dirname=None):
    output_path = get_output_path(candidate_tree_path, dirname)
    K = 5
    events = detect_events_given_path(candidate_tree_path, K)
    d3_events = [to_d3_graph(e)
                 for e in events]
    json_dump(d3_events, output_path)


if __name__ == '__main__':
    import sys
    run(sys.argv[1], sys.argv[2])
