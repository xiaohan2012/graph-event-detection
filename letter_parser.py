import re
import numpy as np
import codecs
import pandas as pd

from datetime import datetime, timedelta
from glob import glob
from copy import copy
from fysom import Fysom


def get_action(l, fst):
    l = l.strip()
    if fst.current == 'C' and l.startswith('<Q_'):
        return 'letter_end'
    elif l.startswith('<Q_'):
        return '<q'
    elif fst.current == 'Q' and l.startswith('{ED'):
        return '{ed'
    elif l.startswith('AUTHOR:'):
        return 'author'
    elif l.startswith('RECIPIENT:'):
        return 'recipient'
    elif len(l) > 0:
        return 'non_empty'
    else:
        return 'empty'


year_regexp = re.compile('(\d{4})')
author_regexp = re.compile('AUTHOR:(\w+)')
recipient_regexp = re.compile('RECIPIENT:([\w&]+)')
ymd_regexp = re.compile(
    '(\?|\d{1,2})[^_\d]*_[^_\d]*(\?|JANUARY|February|March|April|May|June|July|August|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\D*_\D*(\d{4})',
    re.I)
content_regexp = re.compile('([A-Z]+,\d{1,3}.\d{3}.\d{1,3})|(\{.*?\})|(=)|(<.*?>)|(\$)')

def get_year(l):
    return int(year_regexp.findall(l)[0])


def get_author(l):
    return author_regexp.findall(l)[0]


def get_recipient(l):
    return recipient_regexp.findall(l)[0]


def get_year_month_day(l):
    try:
        day, month, year = ymd_regexp.findall(l)[0]
        if day == '?':
            day = 1
        else:
            day = int(day)

        if  month == '?':
            month = 1
        else:
            month = datetime.strptime(month, '%B').month

        year = int(year)
        return year, month, day
    except IndexError:
        return None, None, None


def process_content_line(l):
    return content_regexp.sub('', l)

date = {}


def onQ(e):
    global date
    date = {'month': 1, 'day': 1}
    date['year'] = get_year(e.line)

    e.letter['datetime'] = None
    e.letter['subject'] = ''
    e.letter['body'] = ''

def onA(e):
    global date
    e.letter['sender_id'] = get_author(e.line)


def onR(e):
    e.letter['recipient_ids'] = [get_recipient(e.line)]


def onC(e):
    e.letter['body'] += process_content_line(e.line)

def onED(e):
    global date
    year, month, day = get_year_month_day(e.line)
    if year:
        date['year'] = year
        if month:
            date['month'] = month
        if day:
            if day > 31:
                date['day'] = 1
            else:
                date['day'] = day

def onletter_end(e):
    global date
    try:
        e.letter['datetime'] = datetime(**date)
    except ValueError:
        print date
        raise
    e.letters.append(copy(e.letter))


fst = Fysom(
    initial='S',
    events=[
        ('non_empty', 'S', 'S'),
        ('<q', 'S', 'Q'),
        ('{ed', 'Q', 'ED'),
        ('{ed', 'ED', 'ED'),
        ('non_empty', 'ED', 'ED'),
        ('non_empty', 'Q', 'Q'),
        ('author', 'Q', 'A'),
        ('author', 'ED', 'A'),
        ('recipient', 'A', 'R'),
        ('non_empty', 'R', 'L'),
        ('non_empty', 'L', 'C'),
        ('non_empty', 'C', 'C'),
        ('author', 'C', 'A'),
        ('letter_end', 'C', 'Q'),
        ('file_end', 'C', 'T')
    ],
    callbacks={
        'onQ': onQ,
        'onA': onA,
        'onR': onR,
        'onenterED': onED,
        'onreenterED': onED,
        'onenterC': onC,
        'onreenterC': onC,
        'onbeforeletter_end': onletter_end,
        'onbeforefile_end': onletter_end
    }
)


def parse_file(path):
    fst.current = 'S'
    with codecs.open(path, 'r', 'utf8') as f:
        letter = {}
        letters = []
        for i, l in enumerate(f):
            if l.strip():
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

        # the last letter
        fst.file_end(line='',
                     letter=letter,
                     letters=letters)


    return letters


def parse_to_df(data_dir):
    letters = []
    for path in glob(data_dir):
        letters += parse_file(path)

    for i, l in enumerate(letters):
        l['message_id'] = i
    return pd.DataFrame(letters)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('')
    parser.add_argument('--data_dir')
    parser.add_argument('--output_path')

    args = parser.parse_args()

    df = parse_to_df(args.data_dir)
    df.to_pickle(args.output_path)
