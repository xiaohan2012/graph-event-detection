from nose.tools import assert_equal, assert_true

from datetime import datetime as dt
from test_util import make_path
from letter_parser import get_action, fst, get_year, \
    get_author, get_recipient, parse_file, get_year_month_day, \
    process_content_line


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
        '<q',
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
        'letter_end',
        wrapper('<Q_')
   ) 

    fst.current = 'Q'
    assert_equal(
        '{ed',
        wrapper('{ED:ANNE,_COUNTESS_OF_ARUNDEL,_TO_LORD_TREASURER_BURLEIGH.}')
   ) 
    
    
def test_get_year():
    l = '<Q_ALL_A_1579_T_WALLEN> <L_ALLEN_001> <A_WILLIAM_ALLEN> <A-GENDER_MALE>'
    assert_equal(
        1579,
        get_year(l)
    )

def test_get_year_month_day():
    l = '{ED:100._ALLEN_TO_JOHN_ARDEN._ROME,_4_SEPTEMBER_1593.}'
    assert_equal(
        (1593, 9, 4),
        get_year_month_day(l)
        )

def test_get_year_month_day_1():
    l = "{ED:6._EARL_OF_SHREWSBURY'S_LETTERS_TO_WILLIAM_WENTWORTH._[A]}"
    assert_equal(
        (None, None, None),
        get_year_month_day(l)
        )


def test_get_year_month_day_2():
    l = '{ED:Antwerp,_10_November,_1593.}'
    assert_equal(
        (1593, 11, 10),
        get_year_month_day(l)
        )


def test_get_year_month_day_3():
    l = '{ED:?_November_1627.}'
    assert_equal(
        (1627, 11, 1),
        get_year_month_day(l)
        )

def test_get_year_month_day_4():
    l = '{ED:178._GEORGE_CELY_TO_SIR_JOHN_WESTON_[DRAFT]_[?_JULY_1482]}'
    assert_equal(
        (1482, 7, 1),
        get_year_month_day(l)
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


def test_process_content_line():
    l = ' <paren>  yet once to be </paren>  complayne of'
    assert_equal(
        process_content_line(l),
        '   yet once to be   complayne of'
        )

def test_process_content_line_1():
    ls = ('ALLEN,8.001.2', 'ARUNDEL,11.001.2', '{COM:ADDRESSED:}', '{TEXT:shalbe}', )
    for l in ls:
        assert_equal(
            process_content_line(l),
            ''
            )

def test_process_content_line_2():
    ls = ('yo=r=', 'y=u=')
    es = ('yor', 'yu')
    for e, l in zip(es, ls):
        assert_equal(
            process_content_line(l),
            e
            )



def test_parse_file():
    path = make_path('test/data/allen.txt')
    letters = parse_file(path)

    assert_equal(4,
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
        dt(1579, 4, 5),
        l1['datetime']
    )
    assert_true(
        l1['body'].startswith('Mr. Hopkins')
    )

    assert_true(
        l1['body'].endswith("Loven chez Madame d'Hungerford . \n")
    )

    l2 = letters[1]
    assert_equal(
        'WILLIAM_ALLEN',
        l2['sender_id']
    )
    assert_equal(
        ['OWEN_LEWIS'],
        l2['recipient_ids']
    )
    assert_equal(
        dt(1579, 5, 12),
        l2['datetime']
    )
    # print(l2['body'])
    assert_true(
        l2['body'].startswith('Most dearly beloved')
    )

    assert_true(
        l2['body'].endswith('Romae . \n')
    )

    black_list = ('{COM:DIAERESIS_ABOVE_THE_LETTER_e_IN_AUDOENO}',
                 'ALLEN,231.003.172',
                 '<paren>',
                 '</paren>',
                 'Mons=r=',
                 '$1579')
    for l in letters:
        for i in black_list:
            print i
            print l['body']
            assert_true(i not in l['body'])
