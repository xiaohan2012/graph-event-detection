import os
import codecs
import numpy as np
import ujson as json

from nose.tools import assert_equal, with_setup, assert_true

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


def check(output_path):
    with codecs.open(output_path, 'r', 'utf8') as f:
        obj = json.loads(f.read())
        for t in obj:
            assert_true(
                np.any([n.get('event', False)
                        for n in t['nodes']])
            )
    assert_equal(5, len(obj))
    

@with_setup(setup_func, teardown_func)
def test_dump_contexted_events_to_json():
    output_path = os.path.join(
        CURDIR,
        'test/data/tmp/candidate_trees_decompose=False.json'
    )
    run_with_context(
        os.path.join(CURDIR, 'test/data/enron-whole.json'),
        os.path.join(CURDIR, 'test/data/candidate_trees_decompose=False.pkl'),
        os.path.join(CURDIR, 'test/data/tmp')
    )
    check(output_path)


@with_setup(setup_func, teardown_func)
def test_dump_contexted_events_to_json_to_original_graph():
    output_path = os.path.join(
        CURDIR,
        'test/data/tmp/candidate_trees_decompose=False.json'
    )
    run_with_context(
        os.path.join(CURDIR, 'test/data/enron-whole.json'),
        os.path.join(CURDIR, 'test/data/candidate_trees_decompose=False.pkl'),
        os.path.join(CURDIR, 'test/data/tmp'),
        to_original_graph=True
    )
    check(output_path)
