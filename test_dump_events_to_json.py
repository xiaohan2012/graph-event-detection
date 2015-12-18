import os
import codecs
import ujson as json

from nose.tools import assert_equal

from .dump_events_to_json import run
from .test_util import CURDIR


def test_dump_events_to_json():
    output_path = os.path.join(CURDIR, 'test/data/tmp/candidate_trees.json')
    run(os.path.join(CURDIR, 'test/data/candidate_trees.pkl'),
        os.path.join(CURDIR, 'test/data/tmp'))
    with codecs.open(output_path, 'r', 'utf8') as f:
        obj = json.loads(f.read())
    assert_equal(5, len(obj))



