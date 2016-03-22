import unittest
import pandas as pd
from nose.tools import assert_equal, assert_true
from datetime import timedelta as td
from test_util import make_path
from merge_similar_messages import merge_messages_by_single_user, merge_messages


class MergeMessagesTest(unittest.TestCase):
    def setUp(self):
        self.df1 = pd.io.json.read_json(
            make_path('test/data/repeated_messages_interactions.json')
        )

        self.df2 = pd.io.json.read_json(
            make_path('test/data/repeated_messages_interactions_multiple_senders.json')
        )

        self.df3 = pd.io.json.read_json(
            make_path('test/data/repeated_messages_twitter_example.json')
        )

    def _check_mid_year(self, new_df):
        mid_year_messages = new_df[new_df['subject'].map(
            lambda s: s.startswith('Mid-Year'))
        ]

        assert_equal(3,
                     len(mid_year_messages))

        for r_id in[742698, 742699, 545435]:
            assert_true(r_id in mid_year_messages.iloc[1]['recipient_ids'])

    def test_merge_messages_by_single_user(self):
        new_df = merge_messages_by_single_user(self.df1,
                                               max_time_diff=td(weeks=4),
                                               string_similar_threshold=50)
        self._check_mid_year(new_df)

    def test_merge_messages(self):
        new_df = merge_messages(self.df2,
                                max_time_diff=td(weeks=4),
                                string_similar_threshold=50
        )
        self._check_mid_year(new_df)
        assert_true(len(new_df[new_df['message_id'] == 71808]) > 0)

    def test_twitter_case(self):
        df = merge_messages(
            self.df3,
            max_time_diff=td(days=1),
            string_similar_threshold=50,
            time_field='datetime'
        )
        
        assert_equal(1, len(df))
