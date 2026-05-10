"""Desktop UI: menu, game loop, scoreboard, and result overlay.

Screens
-------
- **MenuScreen** — mode selection (vs AI / 2-Player Hotseat)
- **GameScreen** — renders the board, handles clicks, drives AI turns
- **ResultOverlay** — end-of-game result with Play Again / Back to Menu
"""

from __future__ import annotations

import pygame

from src.ai import EASY, MEDIUM, get_move
from src.game import O, X, Board
from src.renderer import draw_cube, highlight_win_line, hit_test

# ---------------------------------------------------------------------------
# Colours / layout constants
# ---------------------------------------------------------------------------

BG_COLOUR = (30, 30, 40)
TEXT_COLOUR = (240, 240, 240)
BUTTON_COLOUR = (60, 60, 80)
BUTTON_HOVER = (80, 80, 110)
BUTTON_TEXT = (255, 255, 255)
OVERLAY_BG = (0, 0, 0, 180)

FPS = 30

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _font(size: int = 28) -> pygame.font.Font:
    """Return a default pygame font at *size*."""
    return pygame.font.Font(None, size)


def _draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    hovered: bool = False,
) -> None:
    """Draw a rounded-rect button with centred text."""
    colour = BUTTON_HOVER if hovered else BUTTON_COLOUR
    pygame.draw.rect(surface, colour, rect, border_radius=8)
    pygame.draw.rect(surface, TEXT_COLOUR, rect, width=2, border_radius=8)
    txt = _font(26).render(label, True, BUTTON_TEXT)
    surface.blit(txt, txt.get_rect(center=rect.center))


def _find_win_cells(board: Board, player: int) -> list[int] | None:
    """Return the first winning line for *player*, or ``None``."""
    from src.game import WIN_LINES

    cells = board.cells
    for a, b, c in WIN_LINES:
        if cells[a] == player and cells[b] == player and cells[c] == player:
            return [a, b, c]
    return None


# ---------------------------------------------------------------------------
# MenuScreen
# ---------------------------------------------------------------------------


class MenuScreen:
    """Mode-selection screen."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self._sub: str | None = None  # None | "ai_diff"

    def run(self) -> tuple[str, str | None]:
        """Block until a mode is chosen. Returns ``(mode, difficulty)``."""
        clock = pygame.time.Clock()

        btn_ai = pygame.Rect(250, 220, 300, 50)
        btn_hot = pygame.Rect(250, 290, 300, 50)
        btn_easy = pygame.Rect(250, 220, 300, 50)
        btn_med = pygame.Rect(250, 290, 300, 50)
        btn_back = pygame.Rect(250, 360, 300, 50)

        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._sub is None:
                        if btn_ai.collidepoint(event.pos):
                            self._sub = "ai_diff"
                        elif btn_hot.collidepoint(event.pos):
                            return ("hotseat", None)
                    else:
                        if btn_easy.collidepoint(event.pos):
                            return ("ai", EASY)
                        if btn_med.collidepoint(event.pos):
                            return ("ai", MEDIUM)
                        if btn_back.collidepoint(event.pos):
                            self._sub = None

            self.screen.fill(BG_COLOUR)
            title = _font(48).render("Tic-Tac-Toe 3D", True, TEXT_COLOUR)
            self.screen.blit(title, title.get_rect(center=(400, 120)))

            if self._sub is None:
                _draw_button(self.screen, btn_ai, "vs AI", btn_ai.collidepoint(mouse))
                _draw_button(self.screen, btn_hot, "2-Player Hotseat", btn_hot.collidepoint(mouse))
            else:
                sub_title = _font(32).render("Select Difficulty", True, TEXT_COLOUR)
                self.screen.blit(sub_title, sub_title.get_rect(center=(400, 180)))
                _draw_button(self.screen, btn_easy, "Easy", btn_easy.collidepoint(mouse))
                _draw_button(self.screen, btn_med, "Medium", btn_med.collidepoint(mouse))
                _draw_button(self.screen, btn_back, "Back", btn_back.collidepoint(mouse))

            pygame.display.flip()
            clock.tick(FPS)


# ---------------------------------------------------------------------------
# ResultOverlay
# ---------------------------------------------------------------------------


class ResultOverlay:
    """Semi-transparent overlay shown after a game ends."""

    def __init__(self, screen: pygame.Surface, message: str) -> None:
        self.screen = screen
        self.message = message

    def run(self) -> str:
        """Block until a button is pressed. Returns ``'again'`` or ``'menu'``."""
        clock = pygame.time.Clock()
        btn_again = pygame.Rect(200, 340, 180, 50)
        btn_menu = pygame.Rect(420, 340, 180, 50)

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)

        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_again.collidepoint(event.pos):
                        return "again"
                    if btn_menu.collidepoint(event.pos):
                        return "menu"

            self.screen.blit(overlay, (0, 0))
            msg = _font(48).render(self.message, True, TEXT_COLOUR)
            self.screen.blit(msg, msg.get_rect(center=(400, 260)))
            _draw_button(self.screen, btn_again, "Play Again", btn_again.collidepoint(mouse))
            _draw_button(self.screen, btn_menu, "Back to Menu", btn_menu.collidepoint(mouse))
            pygame.display.flip()
            clock.tick(FPS)


# ---------------------------------------------------------------------------
# GameScreen
# ---------------------------------------------------------------------------


class GameScreen:
    """Main gameplay screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        mode: str,
        difficulty: str | None,
    ) -> None:
        self.screen = screen
        self.mode = mode
        self.difficulty = difficulty
        self.board = Board()
        self.current_player = X
        self.score: dict[str, int] = {"X": 0, "O": 0, "draws": 0}
        self.game_over = False
        self.winner: int | None = None
        self.win_cells: list[int] | None = None

    # -- scoreboard --------------------------------------------------------

    def _draw_scoreboard(self) -> None:
        font = _font(24)
        labels = [
            f"X: {self.score['X']}",
            f"O: {self.score['O']}",
            f"Draws: {self.score['draws']}",
        ]
        x_start = 20
        for i, text in enumerate(labels):
            surf = font.render(text, True, TEXT_COLOUR)
            self.screen.blit(surf, (x_start, 10 + i * 28))

        turn_text = f"Turn: {'X' if self.current_player == X else 'O'}"
        if self.game_over:
            if self.winner == X:
                turn_text = "X wins!"
            elif self.winner == O:
                turn_text = "O wins!"
            else:
                turn_text = "Draw!"
        turn_surf = font.render(turn_text, True, TEXT_COLOUR)
        self.screen.blit(turn_surf, (650, 10))

    # -- move handling -----------------------------------------------------

    def _check_end(self) -> None:
        """Check win / draw after a move."""
        if self.board.is_winner(X):
            self.game_over = True
            self.winner = X
            self.score["X"] += 1
            self.win_cells = _find_win_cells(self.board, X)
        elif self.board.is_winner(O):
            self.game_over = True
            self.winner = O
            self.score["O"] += 1
            self.win_cells = _find_win_cells(self.board, O)
        elif self.board.is_draw():
            self.game_over = True
            self.winner = None
            self.score["draws"] += 1

    def _apply_ai_move(self) -> None:
        """Let the AI play immediately (O's turn in AI mode)."""
        if self.difficulty is None:
            return
        cell = get_move(self.board, O, self.difficulty)
        self.board.make_move(cell, O)
        self._check_end()
        if not self.game_over:
            self.current_player = X

    def _reset_board(self) -> None:
        """Start a new round, preserving the session score."""
        self.board = Board()
        self.current_player = X
        self.game_over = False
        self.winner = None
        self.win_cells = None

    # -- main loop ---------------------------------------------------------

    def run(self) -> str:
        """Run the game loop. Returns ``'menu'`` when the player exits to menu."""
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not self.game_over
                ):
                    self._handle_click(event.pos)

            # -- draw -------------------------------------------------------
            self.screen.fill(BG_COLOUR)
            draw_cube(self.screen, self.board)
            if self.win_cells:
                highlight_win_line(self.screen, self.win_cells)
            self._draw_scoreboard()
            pygame.display.flip()

            # -- result overlay on game end ---------------------------------
            if self.game_over:
                if self.winner == X:
                    msg = "X wins!"
                elif self.winner == O:
                    msg = "O wins!"
                else:
                    msg = "Draw!"
                choice = ResultOverlay(self.screen, msg).run()
                if choice == "again":
                    self._reset_board()
                else:
                    return "menu"

            clock.tick(FPS)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Process a click at *pos*."""
        cell = hit_test(pos)
        if cell is None:
            return
        if not self.board.make_move(cell, self.current_player):
            return  # cell occupied

        self._check_end()
        if self.game_over:
            return

        # Switch turns
        if self.mode == "ai":
            # AI plays O immediately
            self.current_player = O
            self._apply_ai_move()
        else:
            self.current_player = O if self.current_player == X else X


# ---------------------------------------------------------------------------
# App — top-level router
# ---------------------------------------------------------------------------


class App:
    """Routes between menu and game screens."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def run(self) -> None:
        """Main application loop."""
        while True:
            mode, difficulty = MenuScreen(self.screen).run()
            game = GameScreen(self.screen, mode, difficulty)
            result = game.run()
            # result is always 'menu' — loop back
