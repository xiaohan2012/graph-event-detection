from nose.tools import assert_equal, assert_true

from datetime import datetime as dt
from .test_util import make_path
from .letter_parser import get_action, fst, get_year, \
    get_author, get_recipient, parse_file


def test_get_action():
    wrapper = lambda l: get_action(l, fst)

    for l in ('<B_ALLEN>', '<P_8>'):
        assert_equal(
            'non_empty',
            wrapper(l)
        )
    for l in ('\n', ''):
        assert_equal(
            'empty',
            wrapper(l)
        )

    assert_equal(
        'Q',
        wrapper('<Q_ALL_A_1579_T_WALLEN> <L_ALLEN_001>')
    )

    assert_equal(
        'author',
        wrapper('AUTHOR:WILLIAM_ALLEN:MALE:_:1532:47')
    )
    assert_equal(
        'recipient',
        wrapper('RECIPIENT:RICHARD_HOPKINS:MALE:_:1546?:33?')
    )
    assert_equal(
        'non_empty',
        wrapper('and being discreete and well experimented by their owne long miseryes I doubt not but now or very speedily they will repayre all defalts and')
    )
    fst.current = 'C'
    assert_equal(
        'one_letter_done',
        wrapper('')
   ) 
    
    
def test_get_year():
    l = '<Q_ALL_A_1579_T_WALLEN> <L_ALLEN_001> <A_WILLIAM_ALLEN> <A-GENDER_MALE>'
    assert_equal(
        1579,
        get_year(l)
    )


def test_get_author():
    l = 'AUTHOR:WILLIAM_ALLEN:MALE:_:1532:47'
    assert_equal(
        'WILLIAM_ALLEN',
        get_author(l)
    )


def test_get_recipient():
    l = 'RECIPIENT:RICHARD_HOPKINS:MALE:_:1546?:33?'
    assert_equal(
        'RICHARD_HOPKINS',
        get_recipient(l)
    )


def test_parse_file():
    path = make_path('test/data/allen.txt')
    letters = parse_file(path)
    assert_equal(180,
                 len(letters))

    l1 = letters[0]
    assert_equal(
        'WILLIAM_ALLEN',
        l1['sender_id']
    )
    assert_equal(
        ['RICHARD_HOPKINS'],
        l1['recipient_ids']
    )
    assert_equal(
        dt(1579, 1, 1, 0),
        l1['datetime']
    )
    assert_true(
        l1['body'].startswith('Mr. Hopkins')
    )

    print(l1['body'])
    assert_true(
        l1['body'].endswith('ALLEN,8.001.1\n')
    )

    l2 = letters[1]
    assert_equal(
        'WILLIAM_ALLEN',
        l2['sender_id']
    )
    assert_equal(
        ['RICHARD_HOPKINS'],
        l2['recipient_ids']
    )
    assert_equal(
        dt(1579, 1, 1, 1),
        l2['datetime']
    )
    assert_true(
        l2['body'].startswith('and being')
    )

    assert_true(
        l2['body'].endswith('ALLEN,8.001.2\n')
    )

    assert_equal(
        dt(1593, 1, 1, 3),
        letters[-1]['datetime']
    )
