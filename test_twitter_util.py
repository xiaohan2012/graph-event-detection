from nose.tools import assert_equal
from .twitter_util import process_text


def test_process_text():
    text = 'RT @ecir2016: Domonkos Tikk @domonkostikk is the #ECIR2016 #industryday keynote speaker. \nFind out about his talk here: https://t.co/MBnugw\u2026'
    assert_equal(
        'RT : Domonkos Tikk  is the   '
        'keynote speaker. \nFind out about his talk here: \u2026',
        process_text(text)
    )
