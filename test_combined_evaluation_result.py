import pandas as pd
import numpy as np
from nose.tools import assert_equal
from numpy.testing import assert_almost_equal
from combine_evaluation_results import combine


def test_combine():
    columns = [1, 2]
    index = ['a', 'b']

    def make_data(multiplier):
        return pd.DataFrame(np.ones((2, 2)) * multiplier,
                            columns=columns,
                            index=index
        )
    r1 = {'m1': make_data(2),
          'm2': make_data(0)}
    r2 = {'m1': make_data(1),
          'm2': make_data(2)}
    r = combine([r1, r2])
    assert_equal(['m1', 'm2'], r.keys())
    
    assert_almost_equal(
        np.ones((2, 2)) * 1.5,
        r['m1'].as_matrix()
    )
    
    assert_almost_equal(
        np.ones((2, 2)) * 1.,
        r['m2'].as_matrix()
    )


def test_combine_with_nan():
    columns = [1, 2]
    index = ['a', 'b']

    def make_data(multiplier):
        return pd.DataFrame(np.ones((2, 2)) * multiplier,
                            columns=columns,
                            index=index
        )
    d = make_data(2)
    d[2]['a'] = np.nan
    r1 = {'m1': d,
          'm2': make_data(0)}
    r2 = {'m1': make_data(1),
          'm2': make_data(2)}
    r = combine([r1, r2])
    assert_equal(['m1', 'm2'], r.keys())
    
    assert_almost_equal(
        np.asarray([[1.5, 1], [1.5, 1.5]]),
        # np.ones((2, 2)) * 1.5,
        r['m1'].as_matrix()
    )
    
    assert_almost_equal(
        np.ones((2, 2)) * 1.,
        r['m2'].as_matrix()
    )
