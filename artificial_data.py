# simulate interactions

import random
import math
import numpy as np
import networkx as nx
import cPickle as pkl

from scipy.spatial.distance import cosine

from experiment_util import weighted_choice
from dag_util import get_roots
from interactions import InteractionsUtil as IU
from experiment_util import get_number_and_percentage, \
    experiment_signature


def random_topic(n_topics, topic_noise=0.0001, taboo_topics=set()):
    taboo_topics = set(taboo_topics)
    while True:
        main_topic = np.random.choice(np.arange(n_topics))
        if main_topic not in taboo_topics:
            break
        
    dirich_alpha = np.zeros(n_topics)
    dirich_alpha[main_topic] = 1
    dirich_alpha += np.random.uniform(0, topic_noise, n_topics)
    dirich_alpha /= dirich_alpha.sum()
    return np.random.dirichlet(dirich_alpha), main_topic


def random_topic_distribution(n_topics):
    raw_vect = np.random.random(n_topics)
    return raw_vect / raw_vect.sum()


def gen_event_with_known_tree_structure(event_size, participants,
                                        start_time, end_time,
                                        event_topic_param,
                                        topic_noise,
                                        alpha, tau,
                                        forward_proba,
                                        reply_proba,
                                        create_new_proba):
    n_participants = len(participants)
    time_step = (end_time - start_time) / float(event_size)
    if time_step < 1:
        # raise ValueError('time_step should be larger than 1 ({}-{}) / {}'.format(
        #     end_time,
        #     start_time,
        #     event_size
        # ))
        print("timestemp < 1")

    tree = nx.DiGraph()
    for i in xrange(event_size):
        time = start_time + time_step * (i+1)
        if tree.number_of_nodes() == 0:
            rand_inds = np.random.permutation(n_participants)
            sender_id = participants[rand_inds[0]]
            recipient_id = participants[rand_inds[1]]
        else:
            # sample a node to connect
            # weighted by degree and recency
            nodes = tree.nodes()
            out_degree = np.asarray([tree.out_degree(n)
                                     for n in nodes])

            recency = np.asarray([time - tree.node[n]['timestamp']
                                  for n in nodes])
            weights = alpha * out_degree + np.power(tau, recency)
            parent = weighted_choice(zip(nodes, weights))[0]

            # randomly choose the type of connection
            # e.g, forward, reply, create_new
            c_type = weighted_choice(
                [('f', forward_proba),
                 ('r', reply_proba),
                 ('c', create_new_proba)]
            )[0]
            tree.add_edge(parent, i, c_type=c_type)

            if c_type == 'r':
                sender_id = tree.node[parent]['recipient_id']
                recipient_id = tree.node[parent]['sender_id']
            elif c_type == 'f':
                parent_sender_id = tree.node[parent]['sender_id']
                sender_id = tree.node[parent]['recipient_id']
                # print(np.random.permutation(n_participants))
                try:
                    recipient_id = (participants[r_id]
                                    for r_id in np.random.permutation(n_participants)
                                    if participants[r_id] != sender_id and
                                    participants[r_id] != parent_sender_id).next()
                except StopIteration:
                    print('participants', participants)
                    print('sender_id, parent_sender_id', sender_id, parent_sender_id)
            else:
                sender_id = tree.node[parent]['sender_id']
                recipient_id = (participants[r_id]
                                for r_id in np.random.permutation(n_participants)
                                if participants[r_id] != sender_id).next()
        tree.add_node(i)

        # randomly adding white noise
        topics = event_topic_param + np.random.uniform(
            0, topic_noise,
            len(event_topic_param)
        )
        topics /= topics.sum()

        tree.node[i] = {
            'message_id': i,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'timestamp': time,
            'topics': topics
        }
    
    # change int to string
    for n in tree.nodes_iter():
        tree.node[n]['sender_id'] = 'u-{}'.format(tree.node[n]['sender_id'])
        tree.node[n]['recipient_ids'] = ['u-{}'.format(
            tree.node[n]['recipient_id'])
        ]
        del tree.node[n]['recipient_id']
    return tree


def random_events(n_events, event_size_mu, event_size_sigma,
                  n_total_participants, participant_mu, participant_sigma,
                  min_time, max_time, event_duration_mu, event_duration_sigma,
                  n_topics, topic_scaling_factor, topic_noise,
                  alpha, tau,
                  forward_proba,
                  reply_proba,
                  create_new_proba,
                  taboo_topics=set(),
                  accumulate_taboo=False):
    # add main events
    events = []
    taboo_topics = set(taboo_topics)
    
    for i in xrange(n_events):
        # randomly select a topic and add some noise to it
        event = []

        event_topic_param, topic_id = random_topic(
            n_topics,
            topic_noise,
            taboo_topics
        )

        if accumulate_taboo:
            taboo_topics.add(topic_id)

        print('event_topic_param:', event_topic_param)
        event_size = 0
        while event_size <= 0:
            event_size = int(round(
                np.random.normal(event_size_mu, event_size_sigma)
            ))
        assert event_size > 0

        # randomly select participants
        n_participants = 0
        while n_participants <= 2:
            n_participants = int(round(
                np.random.normal(participant_mu, participant_sigma)
            ))
        assert n_participants > 2
        
        participants = np.random.permutation(
            n_total_participants
        )[:n_participants]
        print('participants:', participants)

        # event timespan
        start_time = np.random.uniform(min_time, max_time - event_duration_mu)
        end_time = start_time + np.random.normal(event_duration_mu,
                                                 event_duration_sigma)
        if end_time > max_time:
            end_time = max_time

        event = gen_event_with_known_tree_structure(
            event_size, participants, start_time, end_time,
            event_topic_param,
            topic_noise,
            alpha, tau,
            forward_proba,
            reply_proba,
            create_new_proba
        )

        # some checking
        g = IU.get_meta_graph(
            [event.node[n] for n in event.nodes_iter()],
            decompose_interactions=False,
            remove_singleton=True,
            given_topics=True,
            convert_time=False)
        n_interactions_in_mg = g.number_of_nodes()

        if n_interactions_in_mg == len(event):
            roots = [n
                     for n, d in g.in_degree(g.nodes_iter()).items()
                     if d == 0]
            if len(roots) > 1:
                print(roots)
                for r in roots:
                    print(event[r])
                print("WARNING: roots number {}".format(len(roots)))
                raise
        else:
            print(
                'invalid meta graph. {} < {}'.format(
                    n_interactions_in_mg,
                    len(event)
                ))
            raise
        events.append(event)

    return events, taboo_topics


def random_noisy_interactions(n_noisy_interactions,
                              min_time, max_time,
                              n_total_participants,
                              n_topics, topic_noise,
                              taboo_topics=set()):
    taboo_topics = set(taboo_topics)
    noisy_interactions = []
    # noisy events
    for i in xrange(n_noisy_interactions):
        topic = random_topic_distribution(n_topics)
        sender_id, recipient_id = np.random.permutation(
            n_total_participants
        )[:2]
        
        sender_id, recipient_id = 'u-{}'.format(sender_id), \
                                  'u-{}'.format(recipient_id)

        noisy_interactions.append({
            'sender_id': sender_id,
            'recipient_ids': [recipient_id],
            'timestamp': np.random.uniform(min_time, max_time),
            'topics': topic
        })
    return noisy_interactions


def get_gen_cand_tree_params(e):
    U = np.sum(e[s][t]['c'] for s, t in e.edges_iter())

    roots = get_roots(e)
    timestamps = [e.node[n]['timestamp'] for n in e.nodes_iter()]
    preprune_secs = np.max(timestamps) - np.min(timestamps)
    return {
        'U': U,
        'roots': roots,
        'preprune_secs': math.ceil(preprune_secs)
    }


def make_artificial_data(
        # for main events
        n_events,
        event_size_mu, event_size_sigma,
        participant_mu, participant_sigma,
        # for minor events
        n_minor_events,
        minor_event_size_mu, minor_event_size_sigma,
        minor_event_participant_mu, minor_event_participant_sigma,
        # shared
        n_total_participants,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise,
        n_noisy_interactions, n_noisy_interactions_fraction,
        alpha, tau,
        forward_proba,
        reply_proba,
        create_new_proba,
        dist_func):
    events, taboo_topics = random_events(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise,
        alpha, tau,
        forward_proba,
        reply_proba,
        create_new_proba,
        accumulate_taboo=True
    )

    minor_events, _ = random_events(
        n_minor_events, minor_event_size_mu, minor_event_size_sigma,
        n_total_participants, minor_event_participant_mu,
        minor_event_participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise,
        alpha, tau,
        forward_proba,
        reply_proba,
        create_new_proba,
        taboo_topics=taboo_topics,
        accumulate_taboo=False
    )
    
    (n_noisy_interactions, _) = get_number_and_percentage(
        sum([1 for e in events for _ in e]),
        n_noisy_interactions, n_noisy_interactions_fraction
    )
    noisy_interactions = random_noisy_interactions(
        n_noisy_interactions,
        min_time, max_time,
        n_total_participants,
        n_topics, topic_noise,
        taboo_topics
    )

    event_interactions = [e.node[n] for e in events
                          for n in e.nodes_iter()]
    minor_event_interactions = [e.node[n] for e in minor_events
                                for n in e.nodes_iter()]
    all_interactions = (event_interactions + minor_event_interactions
                        + noisy_interactions)

    # add interaction id
    for i, intr in enumerate(all_interactions):
        intr['message_id'] = i
        intr['topics'] = intr['topics'].tolist()

    # relabel the nodes
    relabeled_events = []
    for e in events:
        mapping = {n: e.node[n]['message_id'] for n in e.nodes_iter()}
        relabeled_events.append(nx.relabel_nodes(e, mapping))

    for e in events:
        e = IU.assign_edge_weights(e, dist_func)

    gen_cand_trees_params = [get_gen_cand_tree_params(e)
                             for e in events]
    return relabeled_events, all_interactions, gen_cand_trees_params


def main():
    import ujson as json
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser('Make sythetic interaction data')
    parser.add_argument('--n_events', type=int, default=10)
    parser.add_argument('--event_size_mu', type=int, default=40)
    parser.add_argument('--event_size_sigma', type=int, default=5)
    parser.add_argument('--participant_mu', type=int, default=5)
    parser.add_argument('--participant_sigma', type=float, default=3)

    parser.add_argument('--n_minor_events', type=int, default=0)
    parser.add_argument('--minor_event_size_mu', type=int, default=10)
    parser.add_argument('--minor_event_size_sigma', type=int, default=1)
    parser.add_argument('--minor_event_participant_mu', type=int, default=4)
    parser.add_argument('--minor_event_participant_sigma', type=float, default=0.1)

    parser.add_argument('--n_total_participants', type=int, default=50)
    parser.add_argument('--min_time', type=int, default=10)
    parser.add_argument('--max_time', type=int, default=1100)
    parser.add_argument('--event_duration_mu', type=int, default=100)
    parser.add_argument('--event_duration_sigma', type=int, default=1)

    parser.add_argument('--n_topics', type=int, default=10)
    parser.add_argument('--topic_scaling_factor', type=float, default=0.5)
    parser.add_argument('--topic_noise', type=float, default=0.1)

    parser.add_argument('--n_noisy_interactions', type=int, default=None)
    parser.add_argument('--n_noisy_interactions_fraction',
                        type=float, default=0.1)
    parser.add_argument('--output_dir', type=str, default='data/synthetic')

    parser.add_argument('--alpha',
                        type=float, default=1.0)
    parser.add_argument('--tau',
                        type=float, default=0.8)
    parser.add_argument('--forward_proba',
                        type=float, default=0.3)
    parser.add_argument('--reply_proba',
                        type=float, default=0.5)
    parser.add_argument('--create_new_proba',
                        type=float, default=0.2)

    parser.add_argument('--result_suffix',
                        default='')
    parser.add_argument('--random_seed',
                        type=int,
                        default=None)    

    args = parser.parse_args()

    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    pprint(vars(args))
    result_suffix = args.result_suffix
    output_dir = args.output_dir

    args_dict = vars(args)
    del args_dict['output_dir']
    del args_dict['result_suffix']
    del args_dict['random_seed']

    events, interactions, gen_cand_tree_params = make_artificial_data(
        dist_func=cosine,
        **args_dict
    )
    sig = experiment_signature(
        n_noisy_interactions_fraction=args.n_noisy_interactions_fraction,
        event_size=args.event_size_mu,
    )
    nx.write_gpickle(events,
                     '{}/events--{}{}.pkl'.format(output_dir, sig,
                                                  result_suffix)
    )
    json.dump(interactions,
              open('{}/interactions--{}{}.json'.format(output_dir, sig,
                                                       result_suffix),
                   'w'))
    pkl.dump(gen_cand_tree_params,
             open('{}/gen_cand_tree_params--{}{}.pkl'.format(output_dir, sig,
                                                             result_suffix),
                  'w'))


if __name__ == '__main__':
    main()
