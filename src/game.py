"""3×3×3 Tic-Tac-Toe game model.

Board cells are indexed as ``z*9 + y*3 + x`` where *x*, *y*, *z* ∈ {0, 1, 2}.
"""

from __future__ import annotations

EMPTY = 0
X = 1
O = 2  # noqa: E741


def _cell(x: int, y: int, z: int) -> int:
    """Return flat index for coordinates (x, y, z)."""
    return z * 9 + y * 3 + x


def _build_win_lines() -> list[tuple[int, int, int]]:
    """Compute all 49 winning three-cell lines on a 3×3×3 board.

    Categories:
      - 27 axis-parallel  (9 along each of x, y, z)
      - 18 face-diagonal  (6 per pair of opposing faces, 3 pairs)
      -  4 space-diagonal  (corner-to-corner through centre)
    """
    lines: list[tuple[int, int, int]] = []
    r = range(3)

    # --- 27 axis-parallel lines ---
    # 9 lines along x-axis (fixed y, z)
    for y in r:
        for z in r:
            lines.append((_cell(0, y, z), _cell(1, y, z), _cell(2, y, z)))
    # 9 lines along y-axis (fixed x, z)
    for x in r:
        for z in r:
            lines.append((_cell(x, 0, z), _cell(x, 1, z), _cell(x, 2, z)))
    # 9 lines along z-axis (fixed x, y)
    for x in r:
        for y in r:
            lines.append((_cell(x, y, 0), _cell(x, y, 1), _cell(x, y, 2)))

    # --- 18 face-diagonal lines (6 per axis pair) ---
    # XY-plane diagonals (fixed z) — 2 diags × 3 z-values = 6
    for z in r:
        lines.append((_cell(0, 0, z), _cell(1, 1, z), _cell(2, 2, z)))
        lines.append((_cell(2, 0, z), _cell(1, 1, z), _cell(0, 2, z)))
    # XZ-plane diagonals (fixed y) — 2 diags × 3 y-values = 6
    for y in r:
        lines.append((_cell(0, y, 0), _cell(1, y, 1), _cell(2, y, 2)))
        lines.append((_cell(2, y, 0), _cell(1, y, 1), _cell(0, y, 2)))
    # YZ-plane diagonals (fixed x) — 2 diags × 3 x-values = 6
    for x in r:
        lines.append((_cell(x, 0, 0), _cell(x, 1, 1), _cell(x, 2, 2)))
        lines.append((_cell(x, 2, 0), _cell(x, 1, 1), _cell(x, 0, 2)))

    # --- 4 space diagonals ---
    lines.append((_cell(0, 0, 0), _cell(1, 1, 1), _cell(2, 2, 2)))
    lines.append((_cell(2, 0, 0), _cell(1, 1, 1), _cell(0, 2, 2)))
    lines.append((_cell(0, 2, 0), _cell(1, 1, 1), _cell(2, 0, 2)))
    lines.append((_cell(2, 2, 0), _cell(1, 1, 1), _cell(0, 0, 2)))

    return lines


WIN_LINES: list[tuple[int, int, int]] = _build_win_lines()


class Board:
    """Mutable 3×3×3 board state."""

    __slots__ = ("cells",)

    def __init__(self) -> None:
        self.cells: list[int] = [EMPTY] * 27

    def empty_cells(self) -> list[int]:
        """Return indices of all unoccupied cells."""
        return [i for i, v in enumerate(self.cells) if v == EMPTY]

    def make_move(self, cell: int, player: int) -> bool:
        """Place *player* marker at *cell*.

        Returns ``True`` on success, ``False`` if the cell is out of range or
        already occupied.
        """
        if cell < 0 or cell >= 27:
            return False
        if self.cells[cell] != EMPTY:
            return False
        self.cells[cell] = player
        return True

    def is_winner(self, player: int) -> bool:
        """Return ``True`` if *player* has completed any of the 49 win lines."""
        cells = self.cells
        return any(
            cells[a] == player and cells[b] == player and cells[c] == player
            for a, b, c in WIN_LINES
        )

    def is_draw(self) -> bool:
        """Return ``True`` when all cells are filled and neither player has won."""
        if EMPTY in self.cells:
            return False
        return not self.is_winner(X) and not self.is_winner(O)

    def copy(self) -> Board:
        """Return a deep copy; mutations on the copy do not affect the original."""
        new = Board()
        new.cells = self.cells[:]
        return new
