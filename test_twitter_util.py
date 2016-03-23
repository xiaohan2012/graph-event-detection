from nose.tools import assert_equal
import pandas as pds

from .test_util import make_path
from .twitter_util import remove_mentions_and_urls


def test_process_text():
    df = pds.read_json(make_path('test/data/tweet_example.json'))
    print(df)
    df = remove_mentions_and_urls(df)
    assert_equal(
        ' domonkos tikk  is the #ecir2016 #industryday '
        'keynote speaker. \nfind out about his talk here: ',
        df.iloc[0]['body']
    )
