# tic-tac-toe (3D edition) SPECIFICATION

> Generated from `vbrief/specification.vbrief.json` — edit that file, not this one.

## Overview

A 3D Tic-Tac-Toe desktop game built with Python and pygame. The board is a 3×3×3 cube (27 cells, 49 win lines) rendered in isometric perspective. Players choose between two modes at game start: vs AI or 2-player hotseat. Three AI difficulty levels are supported: Easy (random valid moves), Medium (heuristic play), and Hard (minimax with alpha-beta pruning — optimal, unbeatable). The session scoreboard tracks wins, losses, and draws across multiple rounds without restarting the app.

## Requirements

### Functional Requirements

- FR-1: Display a 3×3×3 cube in isometric perspective in a pygame desktop window.
- FR-2: Game mode selection screen at start — vs AI or 2-player hotseat; vs AI also selects difficulty.
- FR-3: Players click a visible cell face to place their marker (X or O).
- FR-4: Validate moves — reject occupied cells and re-prompt without interrupting flow.
- FR-5: Detect win conditions across all 49 win lines; display winner with highlighted winning line.
- FR-6: Detect draw (board full, no winner) and display draw result.
- FR-7: AI difficulty — Easy: random valid move; Medium: blocks immediate opponent wins, otherwise random; Hard: minimax with alpha-beta pruning (optimal play).
- FR-8: Session scoreboard visible during play — tracks wins and draws for both players.
- FR-9: "Play Again" button after each round resets board; returns to mode selection after confirming.

### Non-Functional Requirements

- NFR-1: Python 3.10+; only external dependency is pygame (`pip install pygame`).
- NFR-2: All 49 win lines must be covered by unit tests in `tests/`.
- NFR-3: Hard AI must be provably optimal — test that it never loses in a suite of games.
- NFR-4: Click-to-cell mapping must correctly identify the clicked cell in all visible cube orientations.

## Architecture

Four modules:

- `src/game.py` — Board state (27-cell flat list, indexed `z*9+y*3+x`), win detection across all 49 lines, draw detection, move validation, `copy()` for AI search.
- `src/ai.py` — Three difficulty levels: Easy (random), Medium (heuristic block/win), Hard (minimax + alpha-beta pruning). Entry: `get_move(board, player, difficulty) -> int`.
- `src/renderer.py` — Isometric projection `iso_project(x, y, z)`, `draw_cube()`, `draw_marker()`, `hit_test()`, `highlight_win_line()`.
- `src/ui.py` — pygame window, `MenuScreen`, `GameScreen`, `ResultOverlay`, session scoreboard, event loop.
- `main.py` — Entry point: `pygame.init()`, window setup, screen routing.

No external dependencies beyond pygame and Python stdlib.

## Implementation Plan

### Phase 1: Foundation (no dependencies)

#### Subphase 1.1: Game Model

- Task 1.1.1: Define `Board` class — 27-cell flat list, `EMPTY/X/O` markers, `empty_cells()`. (traces: FR-3, FR-4)
  - Dependencies: none
  - Acceptance: instantiation works, `empty_cells()` returns 27 on a new board
- Task 1.1.2: Compute `WIN_LINES` — 27 axis-parallel + 18 face-diagonal + 4 space-diagonal = 49 total. (traces: FR-5, NFR-2)
  - Dependencies: Task 1.1.1
  - Acceptance: `len(WIN_LINES) == 49`; all lines confirmed by visual inspection
- Task 1.1.3: Implement `is_winner(player)` and `is_draw()`. (traces: FR-5, FR-6)
  - Dependencies: Task 1.1.2
  - Acceptance: returns correct result for hand-crafted win/draw boards
- Task 1.1.4: Implement `make_move(cell, player)` with validation. (traces: FR-4)
  - Dependencies: Task 1.1.3
  - Acceptance: rejects occupied and out-of-range cells
- Task 1.1.5: Implement `copy()`. (traces: NFR-3)
  - Dependencies: Task 1.1.4
  - Acceptance: mutations to copy do not affect original
- Task 1.1.6: Write `tests/test_game.py` — all 49 win lines, draw, invalid moves. (traces: NFR-2)
  - Dependencies: Tasks 1.1.1–1.1.5
  - Acceptance: `pytest tests/test_game.py` passes; coverage ≥ 90% for `game.py`

### Phase 2: AI Engine (depends on: Phase 1)

- Task 2.1: Easy difficulty — `random.choice(board.empty_cells())`. (traces: FR-7)
  - Dependencies: Phase 1
  - Acceptance: returns a valid empty cell
- Task 2.2: Medium difficulty — block immediate opponent win; else play randomly. (traces: FR-7)
  - Dependencies: Task 2.1
  - Acceptance: `test_ai.py::test_medium_blocks_forced_win` passes
- Task 2.3: Hard difficulty — minimax with alpha-beta pruning on `Board.copy()`. (traces: FR-7, NFR-3)
  - Dependencies: Task 2.2
  - Acceptance: Hard AI never loses in 1000 randomized games; moves in < 2 s on an empty board
- Task 2.4: Write `tests/test_ai.py`. (traces: NFR-3)
  - Dependencies: Tasks 2.1–2.3
  - Acceptance: all AI tests pass

### Phase 3: Isometric Renderer (depends on: Phase 1)

- Task 3.1: Implement `iso_project(x, y, z)` — standard isometric transform. (traces: FR-1, NFR-4)
  - Dependencies: Phase 1
  - Acceptance: returns deterministic (screen_x, screen_y) for all 27 cells
- Task 3.2: Implement `draw_cube(surface, board)` — painter's-algorithm back-to-front polygon draw. (traces: FR-1)
  - Dependencies: Task 3.1
  - Acceptance: all 27 cells rendered without overlap artifacts
- Task 3.3: Implement `draw_marker(surface, cell, player)`. (traces: FR-3)
  - Dependencies: Task 3.2
  - Acceptance: X and O display correctly on each cell face
- Task 3.4: Implement `hit_test(screen_pos, board) -> int|None`. (traces: FR-3, NFR-4)
  - Dependencies: Task 3.1
  - Acceptance: returns correct cell for center-pixel of each cell's top face
- Task 3.5: Implement `highlight_win_line(surface, win_cells)`. (traces: FR-5)
  - Dependencies: Task 3.2
  - Acceptance: winning 3 cells visually highlighted
- Task 3.6: Write `tests/test_renderer.py` — hit_test for all 27 cell centers. (traces: NFR-4)
  - Dependencies: Tasks 3.1–3.5
  - Acceptance: all 27 hit-test assertions pass (headless surface)

### Phase 4: Desktop UI & Game Flow (depends on: Phases 2 + 3)

- Task 4.1: `main.py` — `pygame.init()`, 800×600 window, title, main loop skeleton. (traces: FR-1, NFR-1)
  - Dependencies: Phases 2 + 3
  - Acceptance: window opens and closes cleanly
- Task 4.2: `MenuScreen` — vs AI (with difficulty sub-selection) and 2-Player Hotseat buttons. (traces: FR-2)
  - Dependencies: Task 4.1
  - Acceptance: both modes reachable; difficulty recorded for AI mode
- Task 4.3: `GameScreen` — render cube, current turn label, scoreboard. (traces: FR-1, FR-8)
  - Dependencies: Task 4.2
  - Acceptance: cube renders; turn indicator updates after each move
- Task 4.4: Click handling — `hit_test → make_move → is_winner/is_draw`. (traces: FR-3, FR-4, FR-5, FR-6)
  - Dependencies: Task 4.3
  - Acceptance: full round plays to win or draw without error
- Task 4.5: `ResultOverlay` — winner/draw message, Play Again button, Back to Menu after 3+ rounds. (traces: FR-9)
  - Dependencies: Task 4.4
  - Acceptance: scoreboard increments; Play Again resets board; Back to Menu returns to `MenuScreen`
- Task 4.6: `pygame.QUIT` handler. (traces: NFR-1)
  - Dependencies: Task 4.1
  - Acceptance: window closes cleanly on X button

## Testing Strategy

Unit tests (pytest) in `tests/`:
- `test_game.py` — all 49 win lines, draw detection, move validation, copy()
- `test_ai.py` — Easy always returns valid move; Medium blocks forced wins; Hard never loses in 1000 games
- `test_renderer.py` — hit_test returns correct cell for all 27 cell-center pixels (headless pygame surface)

Integration: manual playthroughs of both game modes on Windows. Coverage target: ≥ 85% overall.

## Deployment

```
pip install pygame
python main.py
```

Package layout:
```
tic-tac-toe/
  main.py
  requirements.txt        # pygame
  src/
    game.py
    ai.py
    renderer.py
    ui.py
  tests/
    test_game.py
    test_ai.py
    test_renderer.py
  docs/
    SPECIFICATION.md
```
