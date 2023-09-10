from cube_env.helpers.utils import Stack

def test_new_stack_is_empty():
    st = Stack()
    assert st.isEmpty()


def test_cannot_pop_stack_is_empty():
    try:
        st = Stack()
        st.pop()
    except RuntimeError as e:
        assert e


def test_after_pushing_one_element_stack_is_not_empty():
    st = Stack()
    st.push(1)
    assert not st.isEmpty()
    st.pop()


def test_after_pushing_and_removing_one_element_stack_is_empty():
    st = Stack()
    st.push(1)
    st.pop()
    assert st.isEmpty()


def test_after_pushing_one_element_pop_returns_last_pushed_element():
    st = Stack()
    st.push(1)
    poppedElement = st.pop()
    assert st.isEmpty()
    assert poppedElement == 1


def test_after_pushing_two_element_pop_returns_last_pushed_element():
    st = Stack()
    st.push(1)
    st.push(2)
    poppedElement = st.pop()
    assert not st.isEmpty()
    assert poppedElement == 2
    poppedElement = st.pop()
    assert st.isEmpty()
    assert poppedElement == 1
