import pytest
from src.main.core.cube import RubikCube3D


def solved_export():
    """Return the export of a fresh solved cube for comparison."""
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


class TestInit:

    def test_cubie_count(self):
        """A 3×3 cube has 26 visible cubies (27 minus the hidden center)."""
        cube = RubikCube3D()
        assert len(cube.cubies) == 26

    def test_starts_solved(self):
        cube = RubikCube3D()
        assert is_solved(cube)

    def test_reset_restores_solved(self):
        cube = RubikCube3D()
        cube.apply_action(0)
        cube.apply_action(4)
        cube.reset()
        assert is_solved(cube)

    def test_export_structure(self):
        """Every exported cubie must have x, y, z and a non-empty colors dict."""
        cube = RubikCube3D()
        for entry in cube.export():
            assert "x" in entry and "y" in entry and "z" in entry
            assert isinstance(entry["colors"], dict)
            assert len(entry["colors"]) > 0

    def test_positions_in_range(self):
        cube = RubikCube3D()
        for c in cube.cubies:
            for coord in c.pos:
                assert coord in (-1, 0, 1)


MOVE_PAIRS = [
    (0, 1),   # U  / U'
    (2, 3),   # D  / D'
    (4, 5),   # F  / F'
    (6, 7),   # B  / B'
    (8, 9),   # L  / L'
    (10, 11), # R  / R'
]

MOVE_NAMES = ["U", "D", "F", "B", "L", "R"]

class TestReversibility:

    @pytest.mark.parametrize("cw, ccw", MOVE_PAIRS)
    def test_move_then_inverse_is_identity(self, cw, ccw):
        cube = RubikCube3D()
        cube.apply_action(cw)
        cube.apply_action(ccw)
        assert is_solved(cube), f"action {cw} followed by {ccw} did not restore solved state"

    @pytest.mark.parametrize("cw, ccw", MOVE_PAIRS)
    def test_four_moves_is_identity(self, cw, ccw):
        """Any face move applied 4 times must return to solved."""
        cube = RubikCube3D()
        for _ in range(4):
            cube.apply_action(cw)
        assert is_solved(cube), f"4× action {cw} did not restore solved state"

    @pytest.mark.parametrize("cw, ccw", MOVE_PAIRS)
    def test_four_inverse_moves_is_identity(self, cw, ccw):
        cube = RubikCube3D()
        for _ in range(4):
            cube.apply_action(ccw)
        assert is_solved(cube), f"4× action {ccw} did not restore solved state"


class TestMovesChangeState:

    @pytest.mark.parametrize("action", list(range(12)))
    def test_single_move_changes_state(self, action):
        cube = RubikCube3D()
        cube.apply_action(action)
        assert not is_solved(cube), f"action {action} left the cube unchanged"


class TestInvalidActions:

    @pytest.mark.parametrize("bad", [-1, 12, 100, -100])
    def test_out_of_range_raises(self, bad):
        cube = RubikCube3D()
        with pytest.raises((ValueError, IndexError)):
            cube.apply_action(bad)


class TestColorIntegrity:

    def test_all_six_colors_present_after_moves(self):
        """No matter what moves are applied, all 6 color indices must still exist."""
        cube = RubikCube3D()
        for action in [0, 4, 8, 2, 6, 10]:
            cube.apply_action(action)

        all_colors = set()
        for c in cube.cubies:
            all_colors.update(c.colors.values())

        assert all_colors == {0, 1, 2, 3, 4, 5}

    def test_color_count_invariant(self):
        """Each color index must appear exactly 9 times (one full face)."""
        from collections import Counter
        cube = RubikCube3D()
        for action in [0, 1, 4, 5, 8, 9]:
            cube.apply_action(action)

        counts = Counter()
        for c in cube.cubies:
            for color in c.colors.values():
                counts[color] += 1

        for color_index in range(6):
            assert counts[color_index] == 9, (
                f"Color {color_index} appears {counts[color_index]} times, expected 9"
            )


class TestKnownSequences:

    def test_known_move_six_times_is_identity(self):
        """R U R' U' repeated 6 times returns to solved (well-known identity)."""
        cube = RubikCube3D()
        known = [10, 0, 11, 1]  # R U R' U'
        for _ in range(6):
            for action in known:
                cube.apply_action(action)
        assert is_solved(cube)