import random
import numpy as np
import itertools
from collections import Counter
import unittest
from nose.tools import assert_equal, assert_true
from .artificial_data import random_topic, random_events, \
    random_noisy_interactions, make_articifial_data


class ArtificialDataTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(123456)
        random.seed(123456)
        self.params = {
            'n_events': 100,
            'event_size_mu': 2000,
            'event_size_sigma': 0.00001,
            'n_total_participants': 20,
            'participant_mu': 10,
            'participant_sigma': 1,
            'min_time': 0,
            'max_time': 100,
            'event_duration_mu': 5,
            'event_duration_sigma': 0.0001,
            'n_topics': 10,
            'topic_scaling_factor': 1000,
            'n_noisy_interactions': 10000
        }

    def seems_like_uniform_distribution(self, array):
        topic_2nd, topic_1st = np.sort(array)[-2:]
        assert_true((topic_1st / topic_2nd) < 10)

    def test_random_topic(self):
        topic = random_topic(10)
        np.testing.assert_almost_equal(1, topic.sum())
        max_2nd, max_1st = np.sort(topic)[-2:]
        assert_true((max_1st / max_2nd) > 10000)

    def test_random_events(self):
        del self.params['n_noisy_interactions']
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
            10,
            mean_n_participants,
            decimal=0
        )
        
        for e in events:
            topic_mean = np.mean([i['topic'] for i in e], axis=0)
            topic_2nd, topic_1st = np.sort(topic_mean)[-2:]
            assert_true((topic_1st / topic_2nd) > 10000)

    def test_random_noisy_interactions(self):
        intrs = random_noisy_interactions(
            self.params['n_noisy_interactions'],
            self.params['min_time'],
            self.params['max_time'],
            self.params['n_total_participants'],
            self.params['n_topics']
        )
        assert_equal(self.params['n_noisy_interactions'],
                     len(intrs))
        topic_mean = np.mean([i['topic'] for i in intrs], axis=0)
        self.seems_like_uniform_distribution(topic_mean)
        
        np.testing.assert_almost_equal(
            50,
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
            assert_true('id' in i)
