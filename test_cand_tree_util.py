import cPickle as pkl
from nose.tools import assert_equal
from .cand_tree_util import remove_self_talking_events
from .test_util import make_path


def test_remove_self_talking_events():
    trees = pkl.load(
        open(make_path('test/data/cand_trees_with_self_talking.pkl'))
    )
    cleaned_trees = remove_self_talking_events(trees)
    assert_equal(0, len(cleaned_trees))
