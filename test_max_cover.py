import unittest
from .max_cover import maximum_k_coverage, argmax_k_coverage
from nose.tools import assert_equal


class MaximumKCoverageTest(unittest.TestCase):
    
    def test_case_independent_sets(self):
        example = [
            set([1, 2, 3]),
            set([4, 5]),
            set([6])
        ]
        
        assert_equal(
            [set([1, 2, 3]), set([4, 5])],
            maximum_k_coverage(example, 2)
        )

    def test_case_overlapping_sets(self):
        example = [
            set([1, 2, 3]),
            set([2, 3, 4]),
            set([4, 5, 6]),
            set([6])
        ]
        
        assert_equal(
            [set([1, 2, 3]), set([4, 5, 6])],
            maximum_k_coverage(example, 2)
        )
        
    def test_empty_sets(self):
        example = []
        assert_equal(
            [],
            maximum_k_coverage(example, 1)
        )

    def test_large_k(self):
        example = [
            set([1, 2, 3]),
            set([2, 3, 4]),
            set([4, 5, 6]),
            set([6])
        ]
        assert_equal(
            example,
            maximum_k_coverage(example, 100)
        )


class ArgmaxKCoverageTest(unittest.TestCase):
    def test_case_independent_sets(self):
        example = [
            set([1, 2, 3]),
            set([4, 5]),
            set([6])
        ]
        
        assert_equal(
            [0, 1],
            argmax_k_coverage(example, 2)
        )

    def test_case_overlapping_sets(self):
        example = [
            set([1, 2, 3]),
            set([2, 3, 4]),
            set([4, 5, 6]),
            set([6])
        ]
        
        assert_equal(
            [0, 2],
            argmax_k_coverage(example, 2)
        )
        
    def test_empty_sets(self):
        example = []
        assert_equal(
            [],
            argmax_k_coverage(example, 1)
        )

    def test_large_k(self):
        example = [
            set([1, 2, 3]),
            set([2, 3, 4]),
            set([4, 5, 6]),
            set([6])
        ]
        assert_equal(
            [0, 1, 2, 3],
            argmax_k_coverage(example, 100)
        )
