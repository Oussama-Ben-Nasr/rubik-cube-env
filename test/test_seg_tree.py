"""
Module Name: range_min.py

Description: This module provides utility functions for performing range minimum queries (RMQ).

Author: Oussama Ben Nasr
Date: October 15, 2023
"""
from cube_env.helpers.range_min import FastRangeMin, SlowRangeMin


def test_range_min_init():
    """
    Test the initialization of FastRangeMin.

    It should create a FastRangeMin instance and check if its size is as expected.
    """
    frm = FastRangeMin(10 * [0])
    assert frm.size() == 10
    assert isinstance(frm, FastRangeMin)


def test_range_min_should_be_zero_initially():
    """
    Test that the range minimum is zero initially.

    It creates a FastRangeMin instance with all zeros and checks if the range minimum
    over the entire array is zero.
    """
    frm = FastRangeMin(10 * [0])
    assert frm.get_min_range(0, 9) == 0


def test_range_min_update_full_array():
    """
    Test updating the full array and checking the minimum.

    It creates a FastRangeMin instance with all zeros, updates a range, and checks if
    the minimum value in a different range is as expected.
    """
    frm = FastRangeMin(8 * [0])
    frm.update_range(0, 7, 1)
    assert frm.get_min_range(3, 5) == 1


def test_range_min_slow_and_fast_without_update_should_match():
    """
    Test that FastRangeMin and SlowRangeMin match without updates.

    It creates instances of FastRangeMin and SlowRangeMin with the same input array
    and checks if their range minimums match without any updates.
    """
    array = [1, 2, 3, 4, 5, 7, 1, 5]
    frs = FastRangeMin(array)
    srs = SlowRangeMin(array)
    frs.update_range(0, frs.size() - 1, 1)
    srs.update_range(0, srs.size() - 1, 1)

    assert frs.get_min_range(0, frs.size() - 1) == srs.get_min_range(0, frs.size() - 1)


def test_range_min_with_update_fast_slow_with_update_should_match():
    """
    Test that FastRangeMin and SlowRangeMin match with updates.

    It creates instances of FastRangeMin and SlowRangeMin with the same input array,
    updates them, and checks if their range minimums match after updates.
    """
    array = [1, 2, 3, 4, 5, 7, 1, 5]
    frs = FastRangeMin(array)
    srs = SlowRangeMin(array)
    frs.update_range(4, 7, 1)
    srs.update_range(4, 7, 1)
    for i in range(len(array)):
        for j in range(i + 1, len(array)):
            frs.update_range(i, j, 1)
            srs.update_range(i, j, 1)
            assert frs.get_min_range(0, frs.size() - 1) == srs.get_min_range(
                0, frs.size() - 1
            )
