import os
import codecs
import ujson as json

from nose.tools import assert_equal, with_setup

from .dump_events_to_json import run
from .dump_contexted_events_to_json import run_with_context
from .test_util import CURDIR, remove_tmp_data


def setup_func():
    "set up test fixtures"


def teardown_func():
    remove_tmp_data(os.path.join(CURDIR, 'test/data/tmp'))
    

@with_setup(setup_func, teardown_func)
def test_dump_events_to_json():
    output_path = os.path.join(CURDIR, 'test/data/tmp/candidate_trees.json')
    run(os.path.join(CURDIR, 'test/data/candidate_trees.pkl'),
        os.path.join(CURDIR, 'test/data/tmp'))
    with codecs.open(output_path, 'r', 'utf8') as f:
        obj = json.loads(f.read())
    assert_equal(5, len(obj))


@with_setup(setup_func, teardown_func)
def test_dump_contexted_events_to_json():
    output_path = os.path.join(CURDIR,
                               'test/data/tmp/candidate_trees_decompose=False.json')
    run_with_context(
        os.path.join(CURDIR, 'test/data/enron-whole.json'),
        os.path.join(CURDIR, 'test/data/candidate_trees_decompose=False.pkl'),
        os.path.join(CURDIR, 'test/data/tmp')
    )
    with codecs.open(output_path, 'r', 'utf8') as f:
        obj = json.loads(f.read())
    assert_equal(5, len(obj))
