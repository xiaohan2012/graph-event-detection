from nose.tools import assert_equal
import pandas as pds

from .test_util import make_path
from .twitter_util import remove_entities


def test_process_text():
    df = pds.read_json(make_path('test/data/tweet_example.json'))
    
    df = remove_entities(df)
    assert_equal(
        ' Domonkos Tikk  is the   '
        'keynote speaker. \nFind out about his talk here: ',
        df.iloc[0]['body']
    )
