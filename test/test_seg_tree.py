"""
This module defines classes for Range Minimum Query using Segment Trees.

It provides an abstract base class `RangeMin` for range minimum query and two implementations:
- `FastRangeMin` for efficient range minimum query.
- `SlowRangeMin` for a slower but straightforward range minimum query.

Example usage is provided with test cases for initializing, querying, and updating the range.

Author: Oussama Ben Nasr
Date: 15/10/2023
"""
from abc import ABC

class RangeMin(ABC):
    """
    Abstract base class for range minimum query.

    Attributes:
        _array (list): The input array for range minimum query.

    Methods:
        __init__(self, array): Initializes the RangeMin object with the input array.
        size(self): Returns the size of the input array.
        get_min_range(self, left, right): Gets the minimum value within a specified range.
        update_range(self, left, right, value): Updates a range in the array with a specified value.
    """

    def __init__(self, array):
        """
        Initializes the RangeMin object with the input array.

        Args:
            array (list): The input array for range minimum query.
        """
        self._array = array

    def size(self):
        """
        Returns the size of the input array.

        Returns:
            int: The size of the input array.
        """
        return len(self._array)

    def get_min_range(self, left, right):
        """
        Gets the minimum value within a specified range.

        Args:
            left (int): The left index of the range.
            right (int): The right index of the range.

        Returns:
            int: The minimum value within the specified range.
        """
        raise NotImplementedError

    def update_range(self, left, right, value):
        """
        Updates a range in the array with a specified value.

        Args:
            left (int): The left index of the range.
            right (int): The right index of the range.
            value (int): The value to be added to the range.
        """
        raise NotImplementedError



class FastRangeMin(RangeMin):
    """
    FastRangeMin class for efficient range minimum query using Segment Trees.

    This class inherits from the RangeMin abstract base class and provides an efficient
    implementation of range minimum query using a Segment Tree.

    Attributes:
        _left (list): Left boundary of tree nodes.
        _right (list): Right boundary of tree nodes.
        _delta (list): Delta values for tree nodes.
        _sum (list): Sum values for tree nodes.

    Methods:
        __init__(self, array): Initializes the FastRangeMin object with the input array.
        get_min_range(self, left, right): Gets the minimum value within a specified range.
        _get_min_range(self, node, left, right): Helper function for range minimum query.
        update_range(self, left, right, value): Updates a range in the array with a specified value.
        _update_range(self, node, left, right, value): Helper function for range updates.
        _init(self, i, left, right): Initializes the Segment Tree nodes.
        _prop(self, node): Propagates delta values in the tree.
        _update(self, node): Updates the tree nodes.

    """
    def __init__(self, array):
        super().__init__(array)
        n = self.size()
        self._left = 4*(n+1) * [0]
        self._right = 4*(n+1) * [0]
        self._delta = 4*(n+1) * [0]
        self._sum = 4*(n+1) * [0]
        self._init(1, 0, n-1)
        for i, elem in enumerate(self._array):
            self.update_range(i, i, elem)

    def get_min_range(self, left, right):
        return self._get_min_range(1, left, right)
    
    def _get_min_range(self, node, left, right):
        if right < self._left[node] or left > self._right[node]:
            return float('inf')
        if left <= self._left[node] and right >= self._right[node]:
            return self._sum[node] + self._delta[node]
        self._prop(node)
        left_min = self._get_min_range(2*node, left, right)
        right_min = self._get_min_range(2*node+1, left, right)
        self._update(node)
        return min(left_min, right_min)

    def update_range(self, left, right, value):
        return self._update_range(1, left, right, value)
    
    def _update_range(self, node, left, right, value):
        if right < self._left[node] or left > self._right[node]:
            return
        if left <= self._left[node] and right >= self._right[node]:
            self._delta[node] += value
            return

        self._prop(node)
        self._update_range(2*node, left, right, value)
        self._update_range(2*node+1, left, right, value)
        self._update(node)
        

    def _init(self, i, left, right):
        self._left[i] = left
        self._right[i] = right
        if right == left:
            return
        mid = (left + right)//2
        self._init(2*i, left, mid)
        self._init(2*i+1, mid+1, right)

    def _prop(self, node):
        self._delta[2*node] += self._delta[node]
        self._delta[2*node+1] += self._delta[node]
        self._delta[node] = 0
    
    def _update(self, node):
        self._sum[node] = min(self._sum[2*node] + self._delta[2*node], self._sum[2*node+1]  + self._delta[2*node+1])



class SlowRangeMin(RangeMin):
    """
    SlowRangeMin class for range minimum query using a simple approach.

    This class inherits from the RangeMin abstract base class and provides a
    straightforward implementation of range minimum query.

    Methods:
        __init__(self, array): Initializes the SlowRangeMin object with the input array.
        get_min_range(self, left, right): Gets the minimum value within a specified range.
        update_range(self, left, right, value): Updates a range in the array with a specified value.
    """
    def get_min_range(self, left, right):
        return min(self._array[left:right+1])

    def update_range(self, left, right, value):
        for i in range(left, right+1):
            self._array[i] += value


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
            assert frs.get_min_range(0, frs.size() - 1) == srs.get_min_range(0, frs.size() - 1)
