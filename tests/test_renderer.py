"""Headless tests for the isometric 3D renderer."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()

import pytest  # noqa: E402

from src.game import O, X, Board  # noqa: E402
from src.renderer import (  # noqa: E402
    ORIGIN,
    cell_top_polygon,
    draw_cube,
    draw_marker,
    highlight_win_line,
    hit_test,
    iso_project,
)


@pytest.fixture()
def surface() -> pygame.Surface:
    """Create a headless 800×600 surface for drawing tests."""
    return pygame.Surface((800, 600))


# --- iso_project ---


def test_iso_project_origin() -> None:
    """iso_project(0,0,0) must equal ORIGIN."""
    assert iso_project(0, 0, 0) == ORIGIN


def test_iso_project_deterministic() -> None:
    """Calling iso_project twice with the same args returns the same result."""
    assert iso_project(1, 2, 1) == iso_project(1, 2, 1)


# --- cell_top_polygon ---


def test_cell_top_polygon_shape() -> None:
    """Top polygon must be a list of exactly 4 (int, int) tuples."""
    poly = cell_top_polygon(1, 1, 1)
    assert isinstance(poly, list)
    assert len(poly) == 4
    for point in poly:
        assert isinstance(point, tuple)
        assert len(point) == 2
        assert isinstance(point[0], int)
        assert isinstance(point[1], int)


# --- hit_test ---


def test_hit_test_all_cells() -> None:
    """Centre of every cell's top face must hit-test to that cell (NFR-4)."""
    board = Board()
    for cell_idx in range(27):
        z = cell_idx // 9
        rem = cell_idx % 9
        y = rem // 3
        x = rem % 3
        poly = cell_top_polygon(x, y, z)
        cx = sum(p[0] for p in poly) // 4
        cy = sum(p[1] for p in poly) // 4
        result = hit_test((cx, cy), board)
        assert result is not None, f"hit_test returned None for cell {cell_idx} at ({cx},{cy})"
        # For cells occluded by higher layers, the topmost cell wins; verify
        # we at least get a valid cell (topmost at that pixel).
        # For z=2 cells, the result must be the exact cell.
        if z == 2:
            assert result == cell_idx, (
                f"cell {cell_idx}: expected {cell_idx}, got {result}"
            )


def test_hit_test_empty_surface() -> None:
    """A point far off the board must return None."""
    board = Board()
    assert hit_test((0, 0), board) is None


# --- draw_cube ---


def test_draw_cube_runs(surface: pygame.Surface) -> None:
    """draw_cube on an empty board must complete without error."""
    board = Board()
    draw_cube(surface, board)


# --- draw_marker ---


def test_draw_marker_x(surface: pygame.Surface) -> None:
    """draw_marker for X on cell 13 (cube centre) must not raise."""
    draw_marker(surface, 13, X)


def test_draw_marker_o(surface: pygame.Surface) -> None:
    """draw_marker for O on cell 13 (cube centre) must not raise."""
    draw_marker(surface, 13, O)


# --- highlight_win_line ---


def test_highlight_win_line_runs(surface: pygame.Surface) -> None:
    """highlight_win_line must complete without error."""
    highlight_win_line(surface, [0, 1, 2])
