import ujson as json
from events import detect_events_given_path
from event_context import extract_event_context
from interactions import InteractionsUtil as IU

from util import json_dump, load_json_by_line
from viz_util import add_subgraph_specific_attributes_to_graph,\
    to_d3_graph
from experiment_util import get_output_path


def run_with_context(interactions_path, candidate_tree_path, dirname=None):
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
        contexted_events.append(
            add_subgraph_specific_attributes_to_graph(
                context_dag, [(e, {'event': True})])
        )
    d3_events = [to_d3_graph(e)
                 for e in events]
    
    print('writing to {}'.format(output_path))
    json_dump(d3_events, output_path)

if __name__ == '__main__':
    import sys
    run_with_context(*sys.argv[1:])
