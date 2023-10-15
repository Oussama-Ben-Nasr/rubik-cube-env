"""
This module provides a simple stack implementation and a function to swap blocks
in a 2D NumPy array.

Author: Oussama Ben Nasr
Date: October 15, 2023
"""
from typing import List
class Stack:
    """
    A simple stack implementation using a list.

    Attributes:
        _elements (List): A list to store stack elements.
    """

    _elements: List = list()

    @property
    def is_empty(self) -> bool:
        """
        Check if the stack is empty.

        Returns:
            bool: True if the stack is empty, False otherwise.
        """
        return len(self._elements) == 0

    @property
    def is_not_empty(self) -> bool:
        """
        Check if the stack is not empty.

        Returns:
            bool: True if the stack is not empty, False otherwise.
        """
        return not self.is_empty

    def push(self, element) -> None:
        """
        Insert an element into the stack.

        Args:
            element: The element to be inserted.
        Returns:
            None
        """
        self._elements.append(element)

    def pop(self) -> int:
        """
        Remove and return the last inserted element in the stack.

        Returns:
            int: The last inserted element.
        Raises:
            RuntimeError: If the stack is empty and cannot be popped.
        """
        if self.is_not_empty:
            return self._elements.pop()
        raise RuntimeError("Cannot pop() on an empty Stack.")
