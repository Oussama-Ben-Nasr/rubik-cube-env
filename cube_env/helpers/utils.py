"""
Module Name: utils.py

Description: This module provides a collection of utility functions for various tasks.

Author: Oussama Ben Nasr
Date: October 15, 2023
"""
import numpy as np


def swap_blocks(array: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> None:
    """
    Swap two blocks in a 2D NumPy array.

    Args:
        array (np.ndarray): The input 2D NumPy array.
        x1 (int): The row index of the first block.
        y1 (int): The column index of the first block.
        x2 (int): The row index of the second block.
        y2 (int): The column index of the second block.

    Returns:
        None: This function modifies the input array in place and doesn't return a value.
    """
    st_value = array[x1, y1]
    nd_value = array[x2, y2]
    array.flat[[range(9 * x1 + y1, 9 * x1 + y1 + 3)]] = nd_value
    array.flat[[range(9 * x2 + y2, 9 * x2 + y2 + 3)]] = st_value
