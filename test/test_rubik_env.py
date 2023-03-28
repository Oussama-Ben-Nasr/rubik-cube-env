import pytest
import numpy as np
from cube_env.rubik_env import RubikCube

def test_initial_state_cube() -> None:
    cube: RubikCube = RubikCube()
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
    assert np.array_equal(cube._state, expected_initial_state)
