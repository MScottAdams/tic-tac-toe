"""Tests for the 3×3×3 Tic-Tac-Toe game model."""

import pytest

from src.game import EMPTY, WIN_LINES, Board, O, X, _cell

# ---------------------------------------------------------------------------
# Sanity: WIN_LINES count
# ---------------------------------------------------------------------------

def test_win_lines_count():
    assert len(WIN_LINES) == 49


def test_win_lines_all_unique():
    normalised = [tuple(sorted(line)) for line in WIN_LINES]
    assert len(set(normalised)) == 49


# ---------------------------------------------------------------------------
# Helper: place three cells for a player and verify win
# ---------------------------------------------------------------------------

def _assert_line_wins(line: tuple[int, int, int], player: int) -> None:
    board = Board()
    for cell in line:
        assert board.make_move(cell, player)
    assert board.is_winner(player)
    # Other player should NOT be detected as winner
    other = O if player == X else X
    assert not board.is_winner(other)


# ---------------------------------------------------------------------------
# Axis-parallel lines (27)
# ---------------------------------------------------------------------------

class TestAxisParallelLines:
    """9 x-axis + 9 y-axis + 9 z-axis = 27 axis-parallel lines."""

    # -- x-axis lines (fixed y, z) --
    @pytest.mark.parametrize("y,z", [(y, z) for y in range(3) for z in range(3)])
    def test_x_axis(self, y: int, z: int):
        line = (_cell(0, y, z), _cell(1, y, z), _cell(2, y, z))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    # -- y-axis lines (fixed x, z) --
    @pytest.mark.parametrize("x,z", [(x, z) for x in range(3) for z in range(3)])
    def test_y_axis(self, x: int, z: int):
        line = (_cell(x, 0, z), _cell(x, 1, z), _cell(x, 2, z))
        assert line in WIN_LINES
        _assert_line_wins(line, O)

    # -- z-axis lines (fixed x, y) --
    @pytest.mark.parametrize("x,y", [(x, y) for x in range(3) for y in range(3)])
    def test_z_axis(self, x: int, y: int):
        line = (_cell(x, y, 0), _cell(x, y, 1), _cell(x, y, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, X)


# ---------------------------------------------------------------------------
# Face-diagonal lines (18)
# ---------------------------------------------------------------------------

class TestFaceDiagonalLines:
    """6 XY + 6 XZ + 6 YZ = 18 face-diagonal lines."""

    # -- XY-plane diags (fixed z) --
    @pytest.mark.parametrize("z", range(3))
    def test_xy_main_diag(self, z: int):
        line = (_cell(0, 0, z), _cell(1, 1, z), _cell(2, 2, z))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    @pytest.mark.parametrize("z", range(3))
    def test_xy_anti_diag(self, z: int):
        line = (_cell(2, 0, z), _cell(1, 1, z), _cell(0, 2, z))
        assert line in WIN_LINES
        _assert_line_wins(line, O)

    # -- XZ-plane diags (fixed y) --
    @pytest.mark.parametrize("y", range(3))
    def test_xz_main_diag(self, y: int):
        line = (_cell(0, y, 0), _cell(1, y, 1), _cell(2, y, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    @pytest.mark.parametrize("y", range(3))
    def test_xz_anti_diag(self, y: int):
        line = (_cell(2, y, 0), _cell(1, y, 1), _cell(0, y, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, O)

    # -- YZ-plane diags (fixed x) --
    @pytest.mark.parametrize("x", range(3))
    def test_yz_main_diag(self, x: int):
        line = (_cell(x, 0, 0), _cell(x, 1, 1), _cell(x, 2, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    @pytest.mark.parametrize("x", range(3))
    def test_yz_anti_diag(self, x: int):
        line = (_cell(x, 2, 0), _cell(x, 1, 1), _cell(x, 0, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, O)


# ---------------------------------------------------------------------------
# Space-diagonal lines (4)
# ---------------------------------------------------------------------------

class TestSpaceDiagonalLines:
    """4 corner-to-corner space diagonals."""

    def test_diag_000_222(self):
        line = (_cell(0, 0, 0), _cell(1, 1, 1), _cell(2, 2, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    def test_diag_200_022(self):
        line = (_cell(2, 0, 0), _cell(1, 1, 1), _cell(0, 2, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, O)

    def test_diag_020_202(self):
        line = (_cell(0, 2, 0), _cell(1, 1, 1), _cell(2, 0, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, X)

    def test_diag_220_002(self):
        line = (_cell(2, 2, 0), _cell(1, 1, 1), _cell(0, 0, 2))
        assert line in WIN_LINES
        _assert_line_wins(line, O)


# ---------------------------------------------------------------------------
# Draw detection
# ---------------------------------------------------------------------------

class TestDraw:
    def test_draw_impossible_on_full_board(self):
        """Any complete 2-colouring of a 3×3×3 board contains a monochromatic
        line among the 49 win lines, so is_draw() must always return False on
        a fully-filled board."""
        board = Board()
        # Fill with an alternating pattern — at least one player always wins.
        for i in range(27):
            board.cells[i] = X if i % 2 == 0 else O
        assert len(board.empty_cells()) == 0
        # A winner must exist, so is_draw() is False.
        assert not board.is_draw()
        assert board.is_winner(X) or board.is_winner(O)

    def test_is_draw_returns_true_when_no_winner(self):
        """Verify the True-path of is_draw() by injecting a board state that
        cannot arise via normal play (using marker value 3 to block lines)."""
        board = Board()
        # Fill all cells with non-EMPTY values using three markers so that
        # no line is monochrome for X(1) or O(2).
        marker3 = 3  # a third value that is neither X nor O
        for i in range(27):
            board.cells[i] = marker3
        # Overwrite a few cells with X and O, but ensure no line is all-X or all-O.
        board.cells[0] = X
        board.cells[1] = O
        assert not board.is_winner(X)
        assert not board.is_winner(O)
        assert board.is_draw()

    def test_not_draw_when_cells_remain(self):
        board = Board()
        assert not board.is_draw()

    def test_not_draw_when_winner_exists(self):
        board = Board()
        # X wins along x-axis at y=0, z=0
        for c in (_cell(0, 0, 0), _cell(1, 0, 0), _cell(2, 0, 0)):
            board.make_move(c, X)
        # Fill the rest with O (doesn't matter for this test)
        for i in range(27):
            if board.cells[i] == EMPTY:
                board.cells[i] = O
        assert board.is_winner(X)
        assert not board.is_draw()


# ---------------------------------------------------------------------------
# make_move validation
# ---------------------------------------------------------------------------

class TestMakeMove:
    def test_valid_move(self):
        board = Board()
        assert board.make_move(0, X)
        assert board.cells[0] == X

    def test_occupied_cell_rejected(self):
        board = Board()
        board.make_move(0, X)
        assert not board.make_move(0, O)
        assert board.cells[0] == X  # unchanged

    def test_out_of_range_negative(self):
        board = Board()
        assert not board.make_move(-1, X)

    def test_out_of_range_too_high(self):
        board = Board()
        assert not board.make_move(27, X)

    def test_empty_cells_shrinks(self):
        board = Board()
        assert len(board.empty_cells()) == 27
        board.make_move(13, X)
        empties = board.empty_cells()
        assert len(empties) == 26
        assert 13 not in empties


# ---------------------------------------------------------------------------
# copy() isolation
# ---------------------------------------------------------------------------

class TestCopy:
    def test_copy_returns_equal_state(self):
        board = Board()
        board.make_move(0, X)
        board.make_move(13, O)
        clone = board.copy()
        assert clone.cells == board.cells

    def test_copy_mutation_does_not_affect_original(self):
        board = Board()
        board.make_move(0, X)
        clone = board.copy()
        clone.make_move(1, O)
        assert board.cells[1] == EMPTY  # original untouched

    def test_original_mutation_does_not_affect_copy(self):
        board = Board()
        clone = board.copy()
        board.make_move(5, X)
        assert clone.cells[5] == EMPTY
