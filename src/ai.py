"""AI opponent for 3x3x3 Tic-Tac-Toe.

Provides two difficulty levels: Easy (random) and Medium (heuristic).
"""

from __future__ import annotations

import random

from src.game import EMPTY, WIN_LINES, Board, O, X

EASY = "easy"
MEDIUM = "medium"


def _opponent(player: int) -> int:
    """Return the opposing player token."""
    return O if player == X else X


def _find_winning_move(board: Board, player: int) -> int | None:
    """Return a cell that wins immediately for *player*, or ``None``."""
    cells = board.cells
    for a, b, c in WIN_LINES:
        ca, cb, cc = cells[a], cells[b], cells[c]
        if ca == player:
            if cb == player and cc == EMPTY:
                return c
            if cc == player and cb == EMPTY:
                return b
        elif cb == player and cc == player and ca == EMPTY:
            return a
    return None


def _easy_move(board: Board) -> int:
    """Return a random empty cell."""
    return random.choice(board.empty_cells())


def _medium_move(board: Board, player: int) -> int:
    """Win if possible, block opponent's win, otherwise random."""
    win = _find_winning_move(board, player)
    if win is not None:
        return win
    block = _find_winning_move(board, _opponent(player))
    if block is not None:
        return block
    return random.choice(board.empty_cells())


def get_move(board: Board, player: int, difficulty: str) -> int:
    """Return the AI's chosen cell index.

    Parameters
    ----------
    board : Board
        Current board state.
    player : int
        The AI player token (``X`` or ``O``).
    difficulty : str
        One of ``"easy"`` or ``"medium"``.

    Raises
    ------
    ValueError
        If *difficulty* is not recognised.
    """
    if difficulty == EASY:
        return _easy_move(board)
    if difficulty == MEDIUM:
        return _medium_move(board, player)
    msg = f"Unknown difficulty: {difficulty!r}"
    raise ValueError(msg)
