# simulate interactions

import random
import numpy as np
import networkx as nx
import itertools

from copy import deepcopy

from experiment_util import weighted_choice
from interactions import InteractionsUtil as IU
from experiment_util import get_number_and_percentage, \
    experiment_signature


def random_topic(n_topics, topic_noise=0.0001):
    main_topic = np.random.choice(np.arange(n_topics))
    dirich_alpha = np.zeros(n_topics)
    dirich_alpha[main_topic] = 1
    dirich_alpha += np.random.uniform(0, topic_noise, n_topics)
    dirich_alpha /= dirich_alpha.sum()
    return np.random.dirichlet(dirich_alpha)


def gen_event(event_size, participants,
              start_time, end_time,
              event_topic_param):
    event = []
    for j in xrange(event_size):
        # how to ensure it's a tree?
        # is a real event necessarily a tree?
        interaction_topic = np.random.dirichlet(event_topic_param)
        sender_id, recipient_id = np.random.permutation(participants)[:2]
        sender_id, recipient_id = 'u-{}'.format(sender_id), \
                                  'u-{}'.format(recipient_id)
        timestamp = np.random.uniform(start_time, end_time)
        event.append({
            'message_id': j,  # will be changed later
            'sender_id': sender_id,
            'recipient_ids': [recipient_id],
            'timestamp': timestamp,
            'topics': interaction_topic
        })
    return event


def gen_event_via_random_people_network(event_size, participants,
                                        start_time, end_time,
                                        event_topic_param):
    """at each iteration, generate a message,
    which is sent by some guy who already spoke
    """
    participants_so_far = set()
    event = []
    time_step = (end_time - start_time) / float(event_size)
    for i in xrange(event_size):
        if len(participants_so_far) == 0:
            participants_so_far.add(random.choice(participants))
        sender_id = random.choice(list(participants_so_far))
        while True:
            recipient_id = random.choice(participants)
            if sender_id != recipient_id:
                break

        participants_so_far.add(recipient_id)
        event.append({
            'message_id': i,  # will be changed later
            'sender_id': 'u-{}'.format(sender_id),
            'recipient_ids': ['u-{}'.format(recipient_id)],
            'timestamp': start_time + time_step * (i+1),
            'topics': np.random.dirichlet(event_topic_param)
        })
    return event


def gen_event_with_known_tree_structure(event_size, participants,
                                        start_time, end_time,
                                        event_topic_param,
                                        alpha, tau,
                                        forward_proba,
                                        reply_proba,
                                        create_new_proba):
    n_participants = len(participants)
    time_step = (end_time - start_time) / float(event_size)
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
            for n in nodes:
                print(tree.node[n])
            recency = np.asarray([time - tree.node[n]['timestamp']
                                  for n in nodes])
            weights = alpha * out_degree + np.power(tau, recency)
            parent = weighted_choice(zip(nodes, weights))[0]
            print('parent', parent)
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
                recipient_id = (participants[r_id]
                                for r_id in np.random.permutation(n_participants)
                                if participants[r_id] != sender_id and
                                participants[r_id] != parent_sender_id).next()
            else:
                print(tree.node[parent])
                sender_id = tree.node[parent]['sender_id']
                recipient_id = (participants[r_id]
                                for r_id in np.random.permutation(n_participants)
                                if participants[r_id] != sender_id).next()
        tree.add_node(i)
        tree.node[i] = {
            'message_id': i,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'timestamp': time,
            'topics': np.random.dirichlet(event_topic_param)
        }
    
    # change int to string
    event = []
    for n in tree.nodes_iter():
        e = tree.node[n]
        e['sender_id'] = 'u-{}'.format(tree.node[n]['sender_id'])
        e['recipient_ids'] = ['u-{}'.format(
            tree.node[n]['recipient_id'])
        ]
        del e['recipient_id']
        event.append(e)
    return event, tree


def random_events(n_events, event_size_mu, event_size_sigma,
                  n_total_participants, participant_mu, participant_sigma,
                  min_time, max_time, event_duration_mu, event_duration_sigma,
                  n_topics, topic_scaling_factor, topic_noise):
    # add main events
    events = []
    for i in xrange(n_events):
        # randomly select a topic and add some noise to it
        event = []

        event_topic_param = topic_scaling_factor * random_topic(n_topics,
                                                                topic_noise)
        event_size = 0
        while event_size <= 0:
            event_size = int(round(
                np.random.normal(event_size_mu, event_size_sigma)
            ))
        assert event_size > 0

        # randomly select participants
        n_participants = 0
        while n_participants <= 1:
            n_participants = int(round(
                np.random.normal(participant_mu, participant_sigma)
            ))
        assert n_participants > 1
        
        participants = np.random.permutation(
            n_total_participants
        )[:n_participants]

        # event timespan
        start_time = np.random.uniform(min_time, max_time)
        end_time = start_time + np.random.normal(event_duration_mu,
                                                 event_duration_sigma)
        if end_time > max_time:
            end_time = max_time

        event = gen_event_via_random_people_network(
            event_size, participants, start_time, end_time,
            event_topic_param
        )

        # some checking
        g = IU.get_meta_graph(
            event,
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

    return events


def random_noisy_interactions(n_noisy_interactions,
                              min_time, max_time,
                              n_total_participants,
                              n_topics, topic_noise):
    noisy_interactions = []
    # noisy events
    for i in xrange(n_noisy_interactions):
        topic = random_topic(n_topics, topic_noise)
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


def make_articifial_data(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise,
        n_noisy_interactions, n_noisy_interactions_fraction):
    events = random_events(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise
    )

    (n_noisy_interactions, _) = get_number_and_percentage(
        sum([1 for e in events for _ in e]),
        n_noisy_interactions, n_noisy_interactions_fraction
    )
    noisy_interactions = random_noisy_interactions(
        n_noisy_interactions,
        min_time, max_time,
        n_total_participants,
        n_topics, topic_noise
    )

    all_interactions = list(itertools.chain(*events)) + noisy_interactions

    # add interaction id
    for i, intr in enumerate(all_interactions):
        intr['message_id'] = i
        intr['topics'] = intr['topics'].tolist()

    return events, all_interactions


def main():
    import ujson as json
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser('Make sythetic interaction data')
    parser.add_argument('--n_events', type=int, default=10)
    parser.add_argument('--event_size_mu', type=int, default=40)
    parser.add_argument('--event_size_sigma', type=int, default=5)

    parser.add_argument('--n_total_participants', type=int, default=50)
    parser.add_argument('--participant_mu', type=int, default=5)
    parser.add_argument('--participant_sigma', type=int, default=3)

    parser.add_argument('--min_time', type=int, default=10)
    parser.add_argument('--max_time', type=int, default=110)
    parser.add_argument('--event_duration_mu', type=int, default=5)
    parser.add_argument('--event_duration_sigma', type=int, default=3)

    parser.add_argument('--n_topics', type=int, default=10)
    parser.add_argument('--topic_scaling_factor', type=int, default=0.5)
    parser.add_argument('--topic_noise', type=int, default=0.1)

    parser.add_argument('--n_noisy_interactions', type=int, default=None)
    parser.add_argument('--n_noisy_interactions_fraction',
                        type=float, default=0.1)
    parser.add_argument('--output_dir', type=str, default='data/synthetic')

    args = parser.parse_args()
    pprint(vars(args))

    output_dir = args.output_dir
    args_dict = vars(args)
    del args_dict['output_dir']

    events, interactions = make_articifial_data(**args_dict)
    sig = experiment_signature(
        n_noisy_interactions_fraction=args.n_noisy_interactions_fraction,
    )
    json.dump(events,
              open('{}/events--{}.json'.format(output_dir, sig), 'w'))
    json.dump(interactions,
              open('{}/interactions--{}.json'.format(output_dir, sig),
                   'w'))


if __name__ == '__main__':
    main()
