"""Tests for the AI engine."""

from __future__ import annotations

import pytest

from src.ai import EASY, MEDIUM, get_move
from src.game import Board, O, X


def test_easy_returns_valid_cell() -> None:
    """Easy AI always returns an index of an empty cell."""
    board = Board()
    board.make_move(0, X)
    board.make_move(1, O)
    board.make_move(13, X)

    empty = board.empty_cells()
    for _ in range(50):
        cell = get_move(board, O, EASY)
        assert cell in empty


def test_medium_takes_winning_move() -> None:
    """Medium AI plays the winning move when one exists."""
    board = Board()
    # X occupies cells 0 and 1; cell 2 completes line (0, 1, 2).
    board.make_move(0, X)
    board.make_move(1, X)
    board.make_move(9, O)

    cell = get_move(board, X, MEDIUM)
    assert cell == 2


def test_medium_blocks_opponent() -> None:
    """Medium AI blocks when the opponent threatens to win next move."""
    board = Board()
    # O occupies cells 0 and 1; cell 2 would win for O.
    board.make_move(0, O)
    board.make_move(1, O)
    board.make_move(13, X)

    cell = get_move(board, X, MEDIUM)
    assert cell == 2


def test_get_move_invalid_difficulty() -> None:
    """get_move raises ValueError for unknown difficulty."""
    board = Board()
    with pytest.raises(ValueError, match="Unknown difficulty"):
        get_move(board, X, "impossible")
