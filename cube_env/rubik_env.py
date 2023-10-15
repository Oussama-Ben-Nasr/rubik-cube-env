"""
This module provides a class to represent the internal state of a Rubik's Cube for Oussama Ben Nasr.

Author: Oussama Ben Nasr
Date: October 15, 2023
"""
from dataclasses import dataclass
import numpy as np
from .helpers.utils import swap_blocks

@dataclass
class RubikCube:
    """
    A class to wrap the internal state of the Rubik's cube.
    """

    _state = np.array(
        [
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [3, 3, 3, 4, 4, 4, 5, 5, 5],
            [3, 3, 3, 4, 4, 4, 5, 5, 5],
            [3, 3, 3, 4, 4, 4, 5, 5, 5],
        ]
    )

    def reset(self) -> None:
        """
        A method that resets Rubik' cube to its initial solved state.
        Input:
            None
        Output:
            None
        """
        self._state = np.array(
            [
                [0, 0, 0, 1, 1, 1, 2, 2, 2],
                [0, 0, 0, 1, 1, 1, 2, 2, 2],
                [0, 0, 0, 1, 1, 1, 2, 2, 2],
                [3, 3, 3, 4, 4, 4, 5, 5, 5],
                [3, 3, 3, 4, 4, 4, 5, 5, 5],
                [3, 3, 3, 4, 4, 4, 5, 5, 5],
            ]
        )

    def apply_action(self, action: int) -> None:
        """
        A method that applies a transformation on Rubik' cube.
        Input:
            Action: An integer from 0 to 11 inclusive
        Output:
            None
        """
        if action == 0:
            swap_blocks(self._state, 0, 0, 0, 6)
            swap_blocks(self._state, 0, 3, 3, 3)
            swap_blocks(self._state, 0, 6, 3, 3)
        elif action == 1:
            swap_blocks(self._state, 0, 0, 3, 3)
            swap_blocks(self._state, 0, 6, 3, 3)
            swap_blocks(self._state, 0, 3, 3, 3)
        elif action == 2:
            swap_blocks(self._state, 2, 0, 2, 6)
            swap_blocks(self._state, 2, 6, 5, 3)
            swap_blocks(self._state, 2, 6, 2, 3)
        elif action == 3:
            swap_blocks(self._state, 2, 0, 5, 3)
            swap_blocks(self._state, 2, 6, 5, 3)
            swap_blocks(self._state, 5, 3, 2, 3)
        elif action == 4:
            swap_blocks(self._state, 3, 0, 3, 3)
            swap_blocks(self._state, 0, 6, 3, 3)
            swap_blocks(self._state, 3, 6, 3, 3)
        elif action == 5:
            swap_blocks(self._state, 3, 0, 3, 3)
            swap_blocks(self._state, 3, 6, 3, 0)
            swap_blocks(self._state, 3, 0, 0, 6)
        elif action == 6:
            swap_blocks(self._state, 5, 0, 5, 3)
            swap_blocks(self._state, 5, 6, 5, 0)
            swap_blocks(self._state, 5, 0, 2, 6)
        elif action == 7:
            swap_blocks(self._state, 2, 6, 5, 6)
            swap_blocks(self._state, 2, 6, 5, 3)
            swap_blocks(self._state, 2, 6, 5, 0)
        elif action == 8:
            swap_blocks(self._state, 0, 3, 3, 6)
            swap_blocks(self._state, 0, 3, 0, 0)
            swap_blocks(self._state, 0, 3, 3, 0)
        elif action == 9:
            swap_blocks(self._state, 0, 0, 3, 6)
            swap_blocks(self._state, 0, 0, 0, 3)
            swap_blocks(self._state, 0, 0, 3, 0)
        elif action == 10:
            swap_blocks(self._state, 2, 0, 5, 6)
            swap_blocks(self._state, 2, 0, 2, 3)
            swap_blocks(self._state, 2, 0, 5, 0)
        elif action == 11:
            swap_blocks(self._state, 2, 3, 5, 6)
            swap_blocks(self._state, 2, 3, 2, 0)
            swap_blocks(self._state, 2, 3, 5, 0)
        else:
            raise ValueError(
                f"Forbidden value {action} for action, action can get values from 0 to 11 inclusive"
            )

    def get_state(self) -> np.ndarray:
        """
        A method that gets Rubik's cube internal state.
        Input:
            Action: An integer from 0 to 11 inclusive
        Output:
            None
        """
        return self._state
