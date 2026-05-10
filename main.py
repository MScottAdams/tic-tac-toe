"""Entry point for 3D Tic-Tac-Toe."""

from __future__ import annotations

import pygame

from src.ui import App


def main() -> None:
    """Initialise pygame and run the application."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tic-Tac-Toe 3D")
    app = App(screen)
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()
