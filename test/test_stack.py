"""
Module Name: utils.py

Description: This module provides a collection of utility functions for various tasks.

Author: Oussama Ben Nasr
Date: October 15, 2023
"""
from cube_env.helpers.stack import Stack


def test_new_stack_is_empty():
    st = Stack()
    assert st.is_empty


def test_cannot_pop_stack_is_empty():
    try:
        st = Stack()
        st.pop()
    except RuntimeError as e:
        assert e


def test_after_pushing_one_element_stack_is_not_empty():
    st = Stack()
    st.push(1)
    assert not st.is_empty
    st.pop()


def test_after_pushing_and_removing_one_element_stack_is_empty():
    st = Stack()
    st.push(1)
    st.pop()
    assert st.is_empty


def test_after_pushing_one_element_pop_returns_last_pushed_element():
    st = Stack()
    st.push(1)
    popped_element = st.pop()
    assert st.is_empty
    assert popped_element == 1


def test_after_pushing_two_element_pop_returns_last_pushed_element():
    st = Stack()
    st.push(1)
    st.push(2)
    popped_element = st.pop()
    assert not st.is_empty
    assert popped_element == 2
    popped_element = st.pop()
    assert st.is_empty
    assert popped_element == 1
