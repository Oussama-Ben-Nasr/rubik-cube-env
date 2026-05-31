import pytest
from unittest.mock import patch
from src.main.core.cube import RubikCube3D

from src.main.core.solver import solution
from src.main.core.consts import code_to_actions


def solved_export():
    """Returns a completely pristine structural baseline reference representation."""
    ref = RubikCube3D()
    return _sorted_export(ref)


def _sorted_export(cube: RubikCube3D):
    return sorted(
        [
            (c["x"], c["y"], c["z"], tuple(sorted(c["colors"].items())))
            for c in cube.export()
        ]
    )


def is_solved(cube: RubikCube3D) -> bool:
    return _sorted_export(cube) == solved_export()

class TestSolverFunctionBehavior:

    @pytest.fixture(autouse=True)
    def clean_cube_instance(self):
        """Provides a fresh isolated 3D instance before every single test run."""
        self.cube = RubikCube3D()
        yield

    def test_function_already_solved_cube(self):
        """Test 1: Validates how the function acts on a raw, pristine cube state."""
        res = solution(self.cube)
        
        assert res["status"] == "solved"
        assert res.get("actions_to_be_executed") == []

    @pytest.mark.parametrize("scramble_moves, expected_mock_output", [
        ([10], "R1"),
        
        ([1], "U3"),
        ([10, 0, 11, 1], "R2 U3 F1 B3")
    ])
    def test_function_string_mapping_generation(self, scramble_moves, expected_mock_output):
        """Test 2: Validates the inversion formatting string generation array structures."""
        for action in scramble_moves:
            self.cube.apply_action(action)

        with patch("twophase.solver.solve", return_value=expected_mock_output):
            res = solution(self.cube)
            
        assert res["status"] == "solved"
        assert res["raw_kociemba_notation"] == expected_mock_output.split(" ")

        generated_actions = res["actions_to_be_executed"]
        assert len(generated_actions) > 0
        
        for text_line in generated_actions:
            assert text_line.startswith("Apply action:")
            assert "corresponding to thee move" in text_line


class TestSolverFunctionEdgeCases:

    def test_function_invalid_or_broken_cube_states(self):
        """Test 3: Validates response patterns if Kociemba outputs an internal validation error string."""
        cube = RubikCube3D()

        with patch("twophase.solver.solve", return_value="Error 8: Geometric facelet mismatch"):
            res = solution(cube)
            
        assert res["status"] == "already_solved_or_invalid"
        assert res.get("actions_to_be_executed") == None

    def test_function_double_moves_split_logic(self):
        """Test 4: Verifies that double layer turn keys ('2') successfully multiply action outputs twice."""
        cube = RubikCube3D()
        cube.apply_action(10)
        cube.apply_action(10)

        with patch("twophase.solver.solve", return_value="R2"):
            res = solution(cube)
            
        actions_list = res["actions_to_be_executed"]
        assert len(actions_list) == 2

        expected_id = code_to_actions["R"]
        assert f"Apply action: {expected_id}" in actions_list[0]
        assert f"Apply action: {expected_id}" in actions_list[1]
