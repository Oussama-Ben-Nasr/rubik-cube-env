import pytest
import numpy as np
from cube_env.rubik_env import RubikCube


@pytest.fixture
def cube_instance() -> RubikCube:
    cube = RubikCube()
    cube.reset()
    return cube


def test_initial_state_cube(cube_instance) -> None:
    expected_initial_state = np.array(
        [
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [0, 0, 0, 1, 1, 1, 2, 2, 2],
            [3, 3, 3, 4, 4, 4, 5, 5, 5],
            [3, 3, 3, 4, 4, 4, 5, 5, 5],
            [3, 3, 3, 4, 4, 4, 5, 5, 5]
        ]
    )
    assert np.array_equal(cube_instance._state, expected_initial_state)


def test_action_0_efffect(cube_instance) -> None:
    expected_action_0_effect = [
        [2, 2, 2, 4, 4, 4, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [3, 3, 3, 0, 0, 0, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(0)
    assert np.array_equal(cube_instance._state, expected_action_0_effect)


def test_action_1_efffect(cube_instance) -> None:
    expected_action_1_effect = [
        [4, 4, 4, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [3, 3, 3, 1, 1, 1, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(1)
    assert np.array_equal(cube_instance._state, expected_action_1_effect)


def test_action_2_efffect(cube_instance) -> None:
    expected_action_2_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [2, 2, 2, 4, 4, 4, 1, 1, 1],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 0, 0, 0, 5, 5, 5]
    ]
    cube_instance.apply_action(2)
    assert np.array_equal(cube_instance._state, expected_action_2_effect)


def test_action_3_efffect(cube_instance) -> None:
    expected_action_3_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [4, 4, 4, 2, 2, 2, 0, 0, 0],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 1, 1, 1, 5, 5, 5]
    ]
    cube_instance.apply_action(3)
    assert np.array_equal(cube_instance._state, expected_action_3_effect)


def test_action_4_efffect(cube_instance) -> None:
    expected_action_4_effect = [
        [0, 0, 0, 1, 1, 1, 3, 3, 3],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [4, 4, 4, 5, 5, 5, 2, 2, 2],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(4)
    assert np.array_equal(cube_instance._state, expected_action_4_effect)


def test_action_5_efffect(cube_instance) -> None:
    expected_action_5_effect = [
        [0, 0, 0, 1, 1, 1, 5, 5, 5],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [2, 2, 2, 3, 3, 3, 4, 4, 4],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(5)
    assert np.array_equal(cube_instance._state, expected_action_5_effect)


def test_action_6_efffect(cube_instance) -> None:
    expected_action_6_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [2, 2, 2, 3, 3, 3, 4, 4, 4]
    ]
    cube_instance.apply_action(6)
    assert np.array_equal(cube_instance._state, expected_action_6_effect)


def test_action_7_efffect(cube_instance) -> None:
    expected_action_7_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 3, 3, 3],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [4, 4, 4, 5, 5, 5, 2, 2, 2]
    ]
    cube_instance.apply_action(7)
    assert np.array_equal(cube_instance._state, expected_action_7_effect)


def test_action_8_efffect(cube_instance) -> None:
    expected_action_8_effect = [
        [5, 5, 5, 3, 3, 3, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 4, 4, 4, 1, 1, 1],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(8)
    assert np.array_equal(cube_instance._state, expected_action_8_effect)


def test_action_9_efffect(cube_instance) -> None:
    expected_action_9_effect = [
        [3, 3, 3, 5, 5, 5, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [1, 1, 1, 4, 4, 4, 0, 0, 0],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5]
    ]
    cube_instance.apply_action(9)
    assert np.array_equal(cube_instance._state, expected_action_9_effect)


def test_action_10_efffect(cube_instance) -> None:
    expected_action_10_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [3, 3, 3, 5, 5, 5, 2, 2, 2],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [1, 1, 1, 4, 4, 4, 0, 0, 0]
    ]
    cube_instance.apply_action(10)
    assert np.array_equal(cube_instance._state, expected_action_10_effect)


def test_action_11_efffect(cube_instance) -> None:
    expected_action_11_effect = [
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [5, 5, 5, 3, 3, 3, 2, 2, 2],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [3, 3, 3, 4, 4, 4, 5, 5, 5],
        [0, 0, 0, 4, 4, 4, 1, 1, 1]
    ]
    cube_instance.apply_action(11)
    assert np.array_equal(cube_instance._state, expected_action_11_effect)


def test_should_raise_on_forbidden_action(cube_instance) -> None:
    with pytest.raises(ValueError, match=r".*from 0 to 11 inclusive"):
        cube_instance.apply_action(12)
    with pytest.raises(ValueError, match=r".*from 0 to 11 inclusive"):
        cube_instance.apply_action(-1)
