import os
import ujson as json
from events import detect_events_given_path
from event_context import extract_event_context
from interactions import InteractionsUtil as IU
from meta_graph import convert_to_original_graph

from util import json_dump, load_json_by_line
from viz_util import add_subgraph_specific_attributes_to_graph,\
    to_d3_graph
from experiment_util import get_output_path


def run_with_context(interactions_path,
                     candidate_tree_path,
                     dirname=None,
                     to_original_graph=False):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    try:
        interactions = json.load(open(interactions_path))
    except ValueError:
        interactions = load_json_by_line(interactions_path)
    interactions = IU.clean_interactions(interactions)

    output_path = get_output_path(candidate_tree_path, dirname)

    K = 5
    events = detect_events_given_path(candidate_tree_path, K)

    contexted_events = []
    for e in events:
        context_dag = extract_event_context(
            interactions, e
        )

        if to_original_graph:
            context_dag = convert_to_original_graph(context_dag)
            e = convert_to_original_graph(e)

        contexted_events.append(
            add_subgraph_specific_attributes_to_graph(
                context_dag, [(e, {'event': True})])
        )
    d3_events = [to_d3_graph(ce)
                 for ce in contexted_events]
    
    print('writing to {}'.format(output_path))
    json_dump(d3_events, output_path)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Dump contexted events to json')
    parser.add_argument('--interactions_path',
                        required=True
                    )
    parser.add_argument('--candidate_tree_path',
                        required=True
    )
    parser.add_argument('--dirname')
    parser.add_argument('--to_original_graph',
                        action='store_true',
                        default=False)
    args = parser.parse_args()
    run_with_context(args.interactions_path,
                     args.candidate_tree_path,
                     args.dirname,
                     args.to_original_graph)
