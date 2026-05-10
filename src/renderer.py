"""Isometric 3D renderer for 3×3×3 Tic-Tac-Toe.

Renders the 27-cell cube using painter's algorithm (back-to-front),
provides click-to-cell hit testing, and highlights winning lines.
"""

from __future__ import annotations

import pygame

from src.game import EMPTY, O, X

# --- Constants ---

TILE_W = 64
TILE_H = 32
ORIGIN = (400, 150)

LAYER_COLOURS: list[tuple[int, int, int]] = [
    (173, 216, 230),  # z=0: light blue
    (144, 238, 144),  # z=1: light green
    (255, 255, 224),  # z=2: light yellow
]

SIDE_DARK_FACTOR = 0.6

MARKER_RED = (220, 40, 40)
MARKER_BLUE = (40, 80, 220)
WIN_COLOUR = (255, 255, 0)


def _darken(colour: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return a darker version of *colour* for side faces."""
    return (
        int(colour[0] * SIDE_DARK_FACTOR),
        int(colour[1] * SIDE_DARK_FACTOR),
        int(colour[2] * SIDE_DARK_FACTOR),
    )


# --- Coordinate helpers ---


def iso_project(x: int, y: int, z: int) -> tuple[int, int]:
    """Map 3D cell coordinates to 2D screen position (top-left of top face)."""
    screen_x = ORIGIN[0] + (x - y) * (TILE_W // 2)
    screen_y = ORIGIN[1] + (x + y) * (TILE_H // 2) - z * TILE_H
    return (screen_x, screen_y)


def cell_top_polygon(x: int, y: int, z: int) -> list[tuple[int, int]]:
    """Return the 4 corners of the top rhombus face for cell (x, y, z)."""
    top = iso_project(x, y, z)
    right = iso_project(x + 1, y, z)
    bottom = iso_project(x + 1, y + 1, z)
    left = iso_project(x, y + 1, z)
    return [top, right, bottom, left]


def _cell_coords(cell: int) -> tuple[int, int, int]:
    """Decompose flat cell index into (x, y, z)."""
    z = cell // 9
    rem = cell % 9
    y = rem // 3
    x = rem % 3
    return x, y, z


def _polygon_centre(poly: list[tuple[int, int]]) -> tuple[int, int]:
    """Return the centroid of a polygon."""
    cx = sum(p[0] for p in poly) // len(poly)
    cy = sum(p[1] for p in poly) // len(poly)
    return cx, cy


# --- Drawing ---


def draw_cube(surface: pygame.Surface, board: object) -> None:
    """Draw the full 3×3×3 isometric cube with markers.

    Uses painter's algorithm: z ascending, then y ascending, then x ascending.
    """
    cells = board.cells  # type: ignore[attr-defined]
    for z in range(3):
        colour = LAYER_COLOURS[z]
        dark = _darken(colour)
        for y in range(3):
            for x in range(3):
                top_poly = cell_top_polygon(x, y, z)
                top, right, bottom, left = top_poly

                # Top face
                pygame.draw.polygon(surface, colour, top_poly)
                pygame.draw.polygon(surface, (0, 0, 0), top_poly, 1)

                # Right side face (right -> bottom, dropped by TILE_H)
                right_side = [
                    right,
                    bottom,
                    (bottom[0], bottom[1] + TILE_H),
                    (right[0], right[1] + TILE_H),
                ]
                pygame.draw.polygon(surface, dark, right_side)
                pygame.draw.polygon(surface, (0, 0, 0), right_side, 1)

                # Left side face (left -> bottom, dropped by TILE_H)
                left_side = [
                    left,
                    bottom,
                    (bottom[0], bottom[1] + TILE_H),
                    (left[0], left[1] + TILE_H),
                ]
                pygame.draw.polygon(surface, dark, left_side)
                pygame.draw.polygon(surface, (0, 0, 0), left_side, 1)

                # Marker
                i = z * 9 + y * 3 + x
                if cells[i] != EMPTY:
                    draw_marker(surface, i, cells[i])


def draw_marker(surface: pygame.Surface, cell: int, player: int) -> None:
    """Draw an X or O marker centred on the top face of *cell*."""
    x, y, z = _cell_coords(cell)
    poly = cell_top_polygon(x, y, z)
    top, right, bottom, left = poly

    if player == X:
        # Two diagonal lines across the top face
        pygame.draw.line(surface, MARKER_RED, top, bottom, 3)
        pygame.draw.line(surface, MARKER_RED, right, left, 3)
    elif player == O:
        # Circle inscribed in the top face
        cx, cy = _polygon_centre(poly)
        # Radius ~ half the shorter span of the rhombus
        radius = min(TILE_W // 2, TILE_H) // 2
        pygame.draw.circle(surface, MARKER_BLUE, (cx, cy), radius, 3)


# --- Hit testing ---


def _point_in_polygon(px: int, py: int, poly: list[tuple[int, int]]) -> bool:
    """Ray-casting point-in-polygon test."""
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def hit_test(screen_pos: tuple[int, int], board: object) -> int | None:
    """Return the cell index whose top face contains *screen_pos*, or None.

    Tests topmost (highest z) first; within same z, lowest y then lowest x
    (reverse of painter's order) so the visually topmost cell wins.
    """
    px, py = screen_pos
    for z in range(2, -1, -1):
        for y in range(3):
            for x in range(3):
                poly = cell_top_polygon(x, y, z)
                if _point_in_polygon(px, py, poly):
                    return z * 9 + y * 3 + x
    return None


# --- Win-line highlight ---


def highlight_win_line(surface: pygame.Surface, win_cells: list[int]) -> None:
    """Draw a bright yellow line through the centres of the winning cells."""
    centres = []
    for cell in win_cells:
        x, y, z = _cell_coords(cell)
        poly = cell_top_polygon(x, y, z)
        centres.append(_polygon_centre(poly))
    if len(centres) >= 2:
        pygame.draw.lines(surface, WIN_COLOUR, False, centres, 4)
