# simulate interactions

import numpy as np
import itertools



n_events = 10
event_size_mu = 20
event_size_sigma = 20

n_total_participants = 50
participant_mu = 5
participant_sigma = 5

min_time = 0
max_time = 1000
event_duration_mu = 5
event_duration_sigma = 3

n_topics = 10
topic_scaling_factor = 10

n_noisy_interactions = 100


def random_topic(n_topics, scaling_factor=0.0001):
    main_topic = np.random.choice(np.arange(n_topics))
    dirich_alpha = np.zeros(n_topics)
    dirich_alpha[main_topic] = 1
    dirich_alpha += np.random.uniform(0, scaling_factor, n_topics)
    dirich_alpha /= dirich_alpha.sum()
    return np.random.dirichlet(dirich_alpha)


def random_events(n_events, event_size_mu, event_size_sigma,
                  n_total_participants, participant_mu, participant_sigma,
                  min_time, max_time, event_duration_mu, event_duration_sigma,
                  n_topics, topic_scaling_factor):
    # add main events
    events = []
    for i in xrange(n_events):
        # randomly select a topic and add some noise to it
        event = []

        event_topic_param = topic_scaling_factor * random_topic(n_topics)
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
            interaction_topic = np.random.dirichlet(event_topic_param)
            sender_id, recipient_id = np.random.permutation(participants)[:2]
            timestamp = np.random.uniform(start_time, end_time)
            event.append({
                'sender_id': sender_id,
                'recipient_ids': [recipient_id],
                'timestamp': timestamp,
                'topic': interaction_topic
            })

        events.append(event)
    return events


def random_noisy_interactions(n_noisy_interactions,
                              min_time, max_time,
                              n_total_participants,
                              n_topics):
    noisy_interactions = []
    # noisy events
    for i in xrange(n_noisy_interactions):
        topic = random_topic(n_topics)
        sender_id, recipient_id = np.random.permutation(
            n_total_participants
        )[:2]
        
        noisy_interactions.append({
            'sender_id': sender_id,
            'recipient_ids': [recipient_id],
            'timestamp': np.random.uniform(min_time, max_time),
            'topic': topic
        })
    return noisy_interactions


def make_articifial_data(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor,
        n_noisy_interactions):
    events = random_events(
        n_events, event_size_mu, event_size_sigma,
        n_total_participants, participant_mu, participant_sigma,
        min_time, max_time, event_duration_mu, event_duration_sigma,
        n_topics, topic_scaling_factor
    )
    noisy_interactions = random_noisy_interactions(
        n_noisy_interactions,
        min_time, max_time,
        n_total_participants,
        n_topics
    )

    all_interactions = list(itertools.chain(*events)) + noisy_interactions

    # add interaction id
    for i, intr in enumerate(all_interactions):
        intr['id'] = i
    return events, all_interactions
