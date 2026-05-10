"""Smoke tests for the desktop UI module.

These tests exercise game logic paths in ui.py without requiring a real
display.  SDL is set to ``dummy`` so pygame.Surface works headlessly.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()

from src.ai import EASY, get_move  # noqa: E402
from src.game import EMPTY, Board, O, X  # noqa: E402
from src.ui import GameScreen, _find_win_cells  # noqa: E402


# ---------------------------------------------------------------------------
# Board basics (confirms integration with game module)
# ---------------------------------------------------------------------------


def test_board_initializes() -> None:
    """A new Board has 27 empty cells."""
    board = Board()
    assert len(board.cells) == 27
    assert all(c == EMPTY for c in board.cells)


# ---------------------------------------------------------------------------
# Game flow: X wins
# ---------------------------------------------------------------------------


def test_game_flow_x_wins() -> None:
    """Simulate X completing line [0, 1, 2] and verify win detection."""
    board = Board()
    board.make_move(0, X)
    board.make_move(9, O)
    board.make_move(1, X)
    board.make_move(10, O)
    board.make_move(2, X)

    assert board.is_winner(X) is True
    assert board.is_winner(O) is False
    assert board.is_draw() is False


# ---------------------------------------------------------------------------
# AI move validity
# ---------------------------------------------------------------------------


def test_ai_move_valid() -> None:
    """get_move on a fresh board (easy) returns a valid empty cell."""
    board = Board()
    cell = get_move(board, O, EASY)
    assert 0 <= cell < 27
    assert board.cells[cell] == EMPTY


# ---------------------------------------------------------------------------
# Score tracking (pure Python, no pygame rendering)
# ---------------------------------------------------------------------------


def test_score_tracking() -> None:
    """Manually verify score dict increment logic used by GameScreen."""
    score: dict[str, int] = {"X": 0, "O": 0, "draws": 0}

    # Simulate two X wins and one draw
    score["X"] += 1
    score["X"] += 1
    score["draws"] += 1

    assert score == {"X": 2, "O": 0, "draws": 1}


# ---------------------------------------------------------------------------
# GameScreen unit-level checks
# ---------------------------------------------------------------------------


def test_game_screen_initial_state() -> None:
    """GameScreen starts with empty board, X to play, zeroed score."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)

    assert gs.current_player == X
    assert gs.game_over is False
    assert gs.winner is None
    assert gs.score == {"X": 0, "O": 0, "draws": 0}
    assert len(gs.board.empty_cells()) == 27


def test_game_screen_check_end_x_wins() -> None:
    """_check_end detects X win and updates score."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)

    for cell in (0, 1, 2):
        gs.board.make_move(cell, X)
    gs._check_end()

    assert gs.game_over is True
    assert gs.winner == X
    assert gs.score["X"] == 1


def test_game_screen_check_end_o_wins() -> None:
    """_check_end detects O win and updates score."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "ai", EASY)

    for cell in (0, 1, 2):
        gs.board.make_move(cell, O)
    gs._check_end()

    assert gs.game_over is True
    assert gs.winner == O
    assert gs.score["O"] == 1


def test_game_screen_check_end_draw() -> None:
    """_check_end detects draw (synthetic board with marker 3)."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)

    # Fill with a third marker so no line is monochrome X or O
    for i in range(27):
        gs.board.cells[i] = 3
    gs.board.cells[0] = X
    gs.board.cells[1] = O

    gs._check_end()
    assert gs.game_over is True
    assert gs.winner is None
    assert gs.score["draws"] == 1


def test_game_screen_reset_board() -> None:
    """_reset_board preserves score but clears board state."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)
    gs.score["X"] = 3
    gs.game_over = True
    gs.winner = X

    gs._reset_board()

    assert gs.game_over is False
    assert gs.winner is None
    assert len(gs.board.empty_cells()) == 27
    assert gs.score["X"] == 3  # score preserved


def test_game_screen_apply_ai_move() -> None:
    """_apply_ai_move places O on an empty cell."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "ai", EASY)
    gs.board.make_move(0, X)
    gs.current_player = O

    gs._apply_ai_move()

    # O should have been placed somewhere
    o_cells = [i for i, v in enumerate(gs.board.cells) if v == O]
    assert len(o_cells) == 1


def test_find_win_cells_returns_line() -> None:
    """_find_win_cells returns the winning triple."""
    board = Board()
    for cell in (0, 1, 2):
        board.make_move(cell, X)
    result = _find_win_cells(board, X)
    assert result is not None
    assert set(result) == {0, 1, 2}


def test_find_win_cells_returns_none() -> None:
    """_find_win_cells returns None when no win exists."""
    board = Board()
    assert _find_win_cells(board, X) is None


def test_handle_click_miss() -> None:
    """Clicking off the board does nothing."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)
    gs._handle_click((0, 0))  # far off the board
    assert len(gs.board.empty_cells()) == 27


def test_draw_scoreboard_no_crash() -> None:
    """_draw_scoreboard runs without error on a headless surface."""
    surface = pygame.Surface((800, 600))
    gs = GameScreen(surface, "hotseat", None)
    gs._draw_scoreboard()  # should not raise
