import os
import ujson as json

from nose.tools import assert_equal, assert_true
from pymongo import MongoClient

from .bloomberg_util import (get_companies, has_multiple_companies,
                             transform_article, dump2interactions)
from .test_util import CURDIR


a1 = {'tags': ['topics/companies/A', 'topics/companies/B',
               'topics/not-companies/C', 'D']}
a2 = {'tags': []}
a3 = {'tags': ['topics/companies/A', 'topics/not-companies/B',
               'topics/not-companies/C', 'D']}

article = {
    "_id": "568f9bb34bbfda42419cee68",
    "body": [
        "Apple Inc.'s investors are spooked.",
        "The question investors are asking themselves is whether this time is different."
    ],
    "publish_time": 1452170808,
    "crawled_time": 1452252083,
    "tags": [
        "topics/markets",
        "topics/tech",
        "topics/companies/AAPL:US",
        "topics/iphone"
    ],
    "url": "http://www.bloomberg.com/news/articles/2016-01-07/apple-falls-third-day-as-iphone-woe-cuts-40-billion-in-value",
    "title": "Apple Ends Below $100 for First Time in 14 Months on IPhone Woes"
}


def test_get_companies():
    assert_equal(
        ['A', 'B'],
        get_companies(a1))
    

def test_has_multiple_companies():
    assert_equal(True, has_multiple_companies(a1))
    assert_equal(False, has_multiple_companies(a2))
    assert_equal(False, has_multiple_companies(a3))
    

def test_transform_article():
    a = transform_article(article)
    assert_equal(article['url'], a['message_id'])
    assert_equal(article['title'], a['subject'])
    assert_equal(' '.join(article['body']), a['body'])
    assert_equal(article['publish_time'], a['timestamp'])
    assert_equal(['AAPL:US'], a['participant_ids'])


def test_dump2interactions():
    opath = os.path.join(CURDIR, 'test/data/tmp/tmp.json')
    dump2interactions(MongoClient(serverSelectionTimeoutMS=1)['bloomberg'],
                      'articles_test',
                      opath)
    
    obj = json.load(open(opath))
    assert_equal(827, len(obj))
    for r in obj:
        for f in ('message_id', 'subject', 'body',
                  'timestamp', 'participant_ids'):
            assert_true(f in r)
    os.remove(opath)
