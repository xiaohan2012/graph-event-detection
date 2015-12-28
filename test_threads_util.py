import pandas as pd
from nose.tools import assert_equal, assert_true
from datetime import datetime
from thread_util import add_recipients,\
    KEY_THREAD_ID, KEY_DATETIME, KEY_SENDER_ID, KEY_RECIPIENT_IDS


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
