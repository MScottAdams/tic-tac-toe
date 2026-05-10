# tic-tac-toe (3D edition)

A 3D Tic-Tac-Toe desktop game built with Python and pygame.

The board is a 3×3×3 cube (27 cells, 49 win lines) rendered in isometric perspective.

## Features

- Isometric 3D cube board rendered with pygame
- Two game modes: vs AI or 2-player hotseat
- Three AI difficulty levels: Easy / Medium / Hard (unbeatable minimax)
- Session scoreboard (wins/losses/draws)
- Play Again flow without restarting the app

## Requirements

- Python 3.10+
- pygame

## Installation

```
pip install pygame
python main.py
```

## Development

```
# Install dev dependencies
pip install uv
uv sync

# Run checks
task check

# Run tests only
task test
```

## Specification

See [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) for the full design.
