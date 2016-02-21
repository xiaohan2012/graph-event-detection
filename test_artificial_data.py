import unittest
import random
import numpy as np
import itertools

from collections import Counter
from nose.tools import assert_equal, assert_true

from dag_util import get_roots
from interactions import InteractionsUtil as IU
from artificial_data import random_topic, random_events, \
    random_noisy_interactions, make_articifial_data, \
    gen_event_via_random_people_network


class ArtificialDataTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(123456)
        random.seed(123456)
        self.params = {
            'n_events': 5,
            'event_size_mu': 500,
            'event_size_sigma': 0.00001,
            'n_total_participants': 20,
            'participant_mu': 5,
            'participant_sigma': 1,
            'min_time': 0,
            'max_time': 100,
            'event_duration_mu': 5,
            'event_duration_sigma': 0.0001,
            'n_topics': 10,
            'topic_scaling_factor': 1000,
            'topic_noise': 0.00001,
            'n_noisy_interactions': 1000,
            'n_noisy_interactions_fraction': 0.1
        }

    def seems_like_uniform_distribution(self, array):
        topic_2nd, topic_1st = np.sort(array)[-2:]
        assert_true((topic_1st / topic_2nd) < 10)

    def seems_like_skewed_distribution(self, array):
        max_2nd, max_1st = np.sort(array)[-2:]
        assert_true((max_1st / max_2nd) > 10000)

    def test_random_topic(self):
        topic = random_topic(10, 0.00001)
        np.testing.assert_almost_equal(1, topic.sum())
        self.seems_like_skewed_distribution(topic)

    def test_uniform_topic(self):
        topic = random_topic(10, 1)
        self.seems_like_uniform_distribution(topic)

    def test_random_events(self):
        del self.params['n_noisy_interactions']
        del self.params['n_noisy_interactions_fraction']
        events = random_events(**self.params)
        assert_equal(self.params['n_events'], len(events))

        sizes = np.array([len(e) for e in events])
        np.testing.assert_almost_equal(
            self.params['event_size_mu'],
            np.mean(sizes)
        )

        times = lambda e: [i['timestamp'] for i in e]
        mean_duration = np.mean([max(times(e)) - min(times(e))
                                 for e in events])
        np.testing.assert_almost_equal(
            5,
            mean_duration,
            decimal=0
        )
        
        unique_participants = lambda e: set(itertools.chain(
            *[[i['sender_id']] + i['recipient_ids']
              for i in e]
        ))
        mean_n_participants = np.mean(
            [len(unique_participants(e))
             for e in events]
        )
        np.testing.assert_almost_equal(
            5,
            mean_n_participants,
            decimal=0
        )
        
        for e in events:
            topic_mean = np.mean([i['topics'] for i in e], axis=0)
            topic_2nd, topic_1st = np.sort(topic_mean)[-2:]
            assert_true((topic_1st / topic_2nd) > 10000)

    def test_random_noisy_interactions(self):
        intrs = random_noisy_interactions(
            self.params['n_noisy_interactions'],
            self.params['min_time'],
            self.params['max_time'],
            self.params['n_total_participants'],
            self.params['n_topics'],
            self.params['topic_noise']
        )
        assert_equal(self.params['n_noisy_interactions'],
                     len(intrs))
        topic_mean = np.mean([i['topics'] for i in intrs], axis=0)
        self.seems_like_uniform_distribution(topic_mean)
        
        np.testing.assert_almost_equal(
            49,
            np.mean([i['timestamp'] for i in intrs]),
            decimal=0
        )
        
        freq = Counter(itertools.chain(
            *[[i['sender_id']] + i['recipient_ids']
              for i in intrs]
        ))
        freq = np.array(freq.values(),
                        dtype=np.float64)
        self.seems_like_uniform_distribution(freq / freq.sum())

    def test_make_articifial_data(self):
        events, all_interactions = make_articifial_data(**self.params)
        assert_equal(
            self.params['n_events'],
            len(events)
        )
        assert_equal(
            self.params['event_size_mu'] * self.params['n_events'] +
            self.params['n_noisy_interactions'],
            len(all_interactions)
        )
        for i in all_interactions:
            assert_true('message_id' in i)
            # make sure it's jsonable
            assert_true(isinstance(i['topics'], list))

        for e in events:
            assert_equal(len(e),
                         IU.get_meta_graph(
                             e, decompose_interactions=False,
                             remove_singleton=True,
                             given_topics=True).number_of_nodes())
            for i in e:
                assert_true(isinstance(i['topics'], list))

        for i in all_interactions:
            assert_true(i['sender_id'].startswith('u-'))

    def test_make_articifial_data_with_small_noise_percentage(self):
        fraction = 0.1
        self.params['n_noisy_interactions'] = None
        self.params['n_noisy_interactions_fraction'] = fraction
        events, all_interactions = make_articifial_data(**self.params)
        n_event_interactions = sum([1 for e in events for _ in e])
        total = len(all_interactions)
        assert_equal(
            int(n_event_interactions * fraction),
            total - n_event_interactions
        )

    def test_make_articifial_data_with_large_noise_percentage(self):
        fraction = 1.1
        self.params['n_noisy_interactions'] = None
        self.params['n_noisy_interactions_fraction'] = fraction
        events, all_interactions = make_articifial_data(**self.params)
        n_event_interactions = sum([1 for e in events for _ in e])
        total = len(all_interactions)
        assert_equal(
            int(n_event_interactions * fraction),
            total - n_event_interactions
        )


def test_gen_event_via_random_people_network():
    event_topic_param = random_topic(10, topic_noise=0.0001)
    participants_n = 10
    event_size = 100
    event = gen_event_via_random_people_network(
        event_size,
        participants=range(participants_n),
        start_time=10,
        end_time=110,
        event_topic_param=event_topic_param
    )
    sender_ids = set([e['sender_id'] for e in event])
    recipient_ids = set([e['recipient_ids'][0] for e in event])
    assert_equal(participants_n, len(sender_ids))
    assert_equal(participants_n, len(recipient_ids))

    g = IU.get_meta_graph(
        event,
        decompose_interactions=False,
        remove_singleton=True,
        given_topics=True,
        convert_time=False
    )
    assert_equal(1, len(get_roots(g)))
    assert_equal(event_size, len(event))
