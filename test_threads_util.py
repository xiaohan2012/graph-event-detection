# coding: utf-8
import os
import pandas as pd
from nose.tools import assert_equal, assert_true
from datetime import datetime
from thread_util import add_recipients,\
    add_timestamp,\
    KEY_THREAD_ID, KEY_DATETIME, KEY_SENDER_ID, KEY_RECIPIENT_IDS,\
    collect_user_information, \
    add_recipients_to_islamic_dataset
from test_util import CURDIR


def test_add_recipients():
    data = pd.DataFrame(columns=[KEY_THREAD_ID, KEY_DATETIME, KEY_SENDER_ID,
                                 'other_field'],
                        data={
                            KEY_THREAD_ID: [1, 1, 1, 2],
                            KEY_DATETIME: map(
                                datetime.fromtimestamp,
                                [1284286794, 1284286796,
                                 1284286795, 1284286794]
                            ),
                            KEY_SENDER_ID: ['a', 'a', 'b', 'c'],
                            'other_field': ['', '', '', '']
                        })
    actual = add_recipients(data)
    expected = [['b'], ['a'], ['a', 'b'], []]
    assert_equal(expected, actual[KEY_RECIPIENT_IDS].tolist())
    assert_true('other_field' in actual.columns)


def test_collect_user_information():
    data = pd.DataFrame(columns=['sender_id', 'sender_name'],
                        data={'sender_id': [1, 2, 3, 1, 2],
                              'sender_name': ['One', 'Two', 'Three',
                                              'One', 'Two']})
    actual = collect_user_information(
        data,
        id_field='sender_id',
        other_fields=['sender_name']
    )
    expected = data[:3]
    assert_true(expected.equals(actual))


def test_add_recipients_to_islamic_dataset():
    df = add_recipients_to_islamic_dataset(
        os.path.join(CURDIR, 'test/data/islamic-head-10.txt')
    )
    assert_equal((10, 11), df.shape)
    for c in ('message_id', 'subject', 'body',
              KEY_THREAD_ID, KEY_DATETIME,
              KEY_SENDER_ID, KEY_RECIPIENT_IDS):
        print(c)
        assert_true(c in df.columns)


def test_add_timestamp():
    df = pd.DataFrame(columns=['dt'],
                      data={
                          'dt': map(
                              datetime.fromtimestamp,
                              [1284286794, 1284286796,
                               1284286795, 1284286794]
                          )
                      })
    new_df = add_timestamp(df, dt_field='dt', ts_field="ts")
    for ts, dt in zip(new_df['ts'], df['dt']):
        assert_equal(dt, datetime.fromtimestamp(ts))
