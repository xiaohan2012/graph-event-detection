# simulate interactions

import numpy as np
import itertools


def random_topic(n_topics, topic_noise=0.0001):
    main_topic = np.random.choice(np.arange(n_topics))
    dirich_alpha = np.zeros(n_topics)
    dirich_alpha[main_topic] = 1
    dirich_alpha += np.random.uniform(0, topic_noise, n_topics)
    dirich_alpha /= dirich_alpha.sum()
    return np.random.dirichlet(dirich_alpha)


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

        for j in xrange(event_size):
            # how to ensure it's a tree?
            # is a real event necessarily a tree?
            interaction_topic = np.random.dirichlet(event_topic_param)
            sender_id, recipient_id = np.random.permutation(participants)[:2]
            timestamp = np.random.uniform(start_time, end_time)
            event.append({
                'sender_id': sender_id,
                'recipient_ids': [recipient_id],
                'timestamp': timestamp,
                'topics': interaction_topic
            })

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
        n_noisy_interactions):
    events = random_events(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor, topic_noise
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
    parser = argparse.ArgumentParser('Make sythetic interaction data')
    parser.add_argument('--n_events', type=int, default=10)
    parser.add_argument('--event_size_mu', type=int, default=40)
    parser.add_argument('--event_size_sigma', type=int, default=5)

    parser.add_argument('--n_total_participants', type=int, default=50)
    parser.add_argument('--participant_mu', type=int, default=5)
    parser.add_argument('--participant_sigma', type=int, default=3)

    parser.add_argument('--min_time', type=int, default=0)
    parser.add_argument('--max_time', type=int, default=100)
    parser.add_argument('--event_duration_mu', type=int, default=5)
    parser.add_argument('--event_duration_sigma', type=int, default=3)

    parser.add_argument('--n_topics', type=int, default=10)
    parser.add_argument('--topic_scaling_factor', type=int, default=0.5)
    parser.add_argument('--topic_noise', type=int, default=0.1)

    parser.add_argument('--n_noisy_interactions', type=int, default=100)

    args = parser.parse_args()

    events, interactions = make_articifial_data(**vars(args))
    json.dump(events, open('data/synthetic/events.json', 'w'))
    json.dump(interactions, open('data/synthetic/interactions.json', 'w'))


if __name__ == '__main__':
    main()
