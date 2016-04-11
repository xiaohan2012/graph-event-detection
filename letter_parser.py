import os
import re
import codecs
import pandas as pd

from datetime import datetime, timedelta
from glob import glob
from copy import copy
from fysom import Fysom


def get_action(l, fst):
    l = l.strip()
    if l.startswith('<Q_'):
        return 'Q'
    elif l.startswith('AUTHOR:'):
        return 'author'
    elif l.startswith('RECIPIENT:'):
        return 'recipient'
    elif fst.current == 'C' and len(l) == 0:
        return 'one_letter_done'
    elif len(l) > 0:
        return 'non_empty'
    else:
        return 'empty'


year_regexp = re.compile('(\d{4})')
author_regexp = re.compile('AUTHOR:(\w+)')
recipient_regexp = re.compile('RECIPIENT:([\w&]+)')


def get_year(l):
    return int(year_regexp.findall(l)[0])


def get_author(l):
    return author_regexp.findall(l)[0]


def get_recipient(l):
    return recipient_regexp.findall(l)[0]


date = None


def onQ(e):
    global date
    year = get_year(e.line)
    date = datetime(year, 1, 1)


def onA(e):
    global date
    assert date is not None
    e.letter['datetime'] = date
    e.letter['sender_id'] = get_author(e.line)
    e.letter['subject'] = ''
    e.letter['body'] = ''

    date += timedelta(hours=1)  # need some time difference


def onR(e):
    e.letter['recipient_ids'] = [get_recipient(e.line)]


def onC(e):
    # print('onC', e.line)
    e.letter['body'] += e.line
    # print('body', e.letter['body'])


def onafterone_letter_done(e):
    e.letters.append(copy(e.letter))
    e.letter = {}


fst = Fysom(
    initial='N',
    events=[
        ('author', 'N', 'A'),
        ('non_empty', 'N', 'N'),
        ('empty', 'N', 'N'),
        ('Q', 'N', 'Q'),
        ('non_empty', 'Q', 'N'),
        ('empty', 'Q', 'N'),
        ('recipient', 'A', 'R'),
        ('non_empty', 'R', 'L'),
        ('non_empty', 'L', 'C'),
        ('non_empty', 'C', 'C'),
        ('one_letter_done', 'C', 'N'),
    ],
    callbacks={
        'onQ': onQ,
        'onA': onA,
        'onR': onR,
        'onenterC': onC,
        'onreenterC': onC,
        'onafterone_letter_done': onafterone_letter_done
    }
)


def parse_file(path):
    fst.current = 'N'
    with codecs.open(path, 'r', 'utf8') as f:
        letter = {}
        letters = []
        for i, l in enumerate(f):
            action = get_action(l, fst)
            take_action = getattr(fst, action)
            try:
                take_action(action=action,
                            line=l,
                            letter=letter,
                            letters=letters)
            except:
                print('#line', i+1)
                print(path)
                print l
                raise

            # print('line:', l)
            # print('action:', action)
            # print('fst.current', fst.current)
            # print('\n')

    return letters


def parse_to_df(data_dir):
    letters = []
    for path in glob(data_dir):
        letters += parse_file(path)

    return pd.DataFrame(letters)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('')
    parser.add_argument('--data_dir')
    parser.add_argument('--output_path')

    args = parser.parse_args()

    df = parse_to_df(args.data_dir)
    df.to_json(args.output_path,
               orient='records')
