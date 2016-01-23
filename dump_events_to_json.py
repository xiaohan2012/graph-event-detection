import os
import sys

from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from events import detect_events_given_path
from meta_graph import convert_to_original_graph
from clustering import greedy_clustering_on_graph

from util import json_dump
from viz_util import to_d3_graph
from experiment_util import get_output_path


def run(candidate_tree_path,
        k,
        id2people,
        id2interaction,
        dirname=None,
        to_original_graph=False):

    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    output_path = get_output_path(candidate_tree_path, dirname)

    events = detect_events_given_path(candidate_tree_path, k)
    
    # add people and content
    for e in events:
        for n in e.nodes_iter():
            e.node[n]['sender'] = id2people[e.node[n]['sender_id']]
            e.node[n]['recipients'] = [id2people[id_]
                                       for id_ in e.node[n]['recipient_ids']]
            e.node[n]['subject'] = id2interaction[n]['subject']
            e.node[n]['body'] = id2interaction[n]['body']

        # some simple clustering
        assignment = greedy_clustering_on_graph(e)
        for n in e.nodes_iter():
            e.node[n]['cluster_label'] = assignment[n]

    if to_original_graph:
        events = map(convert_to_original_graph,
                     events)

    d3_events = [to_d3_graph(e)
                 for e in events]
    json_dump(d3_events, output_path)


if __name__ == '__main__':
    import argparse
    from util import load_id2obj_dict

    parser = argparse.ArgumentParser('Dump events to json')
    parser.add_argument('--candidate_tree_path',
                        '-p',
                        required=True
    )
    parser.add_argument('--dirname', '-d', required=True)
    parser.add_argument('--people_path', required=True)
    parser.add_argument('--interactions_path', required=True)
    
    parser.add_argument('-k', type=int, default=10)
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
        args.k,
        load_id2obj_dict(args.people_path, 'id'),
        load_id2obj_dict(args.interactions_path, 'message_id'),
        args.dirname,
        args.to_original_graph)
