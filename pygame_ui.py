"""
pygame_ui.py — Pygame UI Layer for Tic Tac Toe
================================================
Handles ALL rendering, input, and animation.
Game logic lives in game_logic.py; DB calls stay in database.py.

CONNECT YOUR FUNCTIONS HERE:
  • play_game()       → Not called directly; logic is driven cell-by-cell here
  • check_winner()    → Called after every move  (see _check_winner_ui)
  • check_draw()      → Called after every move  (see _check_draw_ui)
  • update_win()      → Called on player win      (see _end_game)
  • update_loss()     → Called on computer win    (see _end_game)
  • update_draw()     → Called on draw            (see _end_game)
  • save_match()      → Called at game end        (see _end_game)
"""

import pygame
import sys
import math
import time

# ── Palette ────────────────────────────────────────────────────────────────
BG          = (15,  17,  26)   # deep navy background
GRID_LINE   = (40,  46,  70)   # subtle grid
CELL_IDLE   = (22,  25,  38)   # cell base
CELL_HOVER  = (32,  38,  62)   # cell hovered
CELL_ACTIVE = (28,  33,  52)   # cell with piece

X_COLOR     = (90, 170, 255)   # electric blue for X
O_COLOR     = (255, 110, 130)  # coral pink for O
WIN_FLASH   = (60, 220, 140)   # emerald highlight on winning cells

POPUP_BG    = (18,  21,  34)
POPUP_BORDER= (55,  65, 100)
BTN_IDLE    = (50,  60, 100)
BTN_HOVER   = (70,  85, 140)
BTN_TEXT    = (220, 225, 255)
TEXT_MAIN   = (210, 215, 240)
TEXT_DIM    = (100, 110, 150)

# ── Layout constants ────────────────────────────────────────────────────────
WIN_W, WIN_H = 600, 660        # extra 60px bottom bar
GRID_MARGIN  = 48
CELL_SIZE    = (WIN_W - GRID_MARGIN * 2) // 3   # 168 px
GRID_TOP     = GRID_MARGIN
LINE_WIDTH   = 3
PIECE_INSET  = 30              # gap between cell edge and drawn piece
CORNER_R     = 14              # cell corner radius


class TicTacToeUI:
    """
    Pygame front-end.  Instantiate once, call run() to start the event loop.

    Parameters
    ----------
    player_name : str
        Name used for all DB calls.
    board : list[str]
        Shared 9-element list (' ', 'X', 'O') from main_game.py.
    check_winner_fn : callable(player: str) -> bool
        Your check_winner() from main.py / game_logic.py.
    check_draw_fn : callable() -> bool
        Your check_draw().
    computer_move_fn : callable() -> None
        Your computer_move() — mutates `board` in-place.
    update_win_fn : callable(name)
        Your update_win().
    update_loss_fn : callable(name)
        Your update_loss().
    update_draw_fn : callable(name)
        Your update_draw().
    save_match_fn : callable(name, result)
        Your save_match().
    reset_board_fn : callable() -> None
        Your reset_board().
    """

    def __init__(
        self,
        player_name,
        board,
        check_winner_fn,
        check_draw_fn,
        computer_move_fn,
        update_win_fn,
        update_loss_fn,
        update_draw_fn,
        save_match_fn,
        reset_board_fn,
    ):
        pygame.init()
        pygame.display.set_caption("Tic Tac Toe")

        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock   = pygame.time.Clock()

        # ── Fonts (system fallback chain) ──────────────────────────────────
        self._init_fonts()

        # ── Game state ─────────────────────────────────────────────────────
        self.player_name     = player_name
        self.board           = board          # shared mutable list
        self.check_winner    = check_winner_fn
        self.check_draw      = check_draw_fn
        self.computer_move   = computer_move_fn
        self.update_win      = update_win_fn
        self.update_loss     = update_loss_fn
        self.update_draw     = update_draw_fn
        self.save_match      = save_match_fn
        self.reset_board     = reset_board_fn

        self.hovered_cell    = -1
        self.game_over       = False
        self.result_text     = ""
        self.winner_cells    = []       # indices of winning triple
        self.player_turn     = True     # True = human, False = computer
        self.computer_delay  = 0.0     # timestamp when computer should move
        self.pieces_anim     = {}      # cell_idx -> anim_progress 0.0-1.0
        self.flash_t         = 0.0     # for winner cell pulsing

        # Restart button rect (drawn in popup)
        self.restart_rect    = pygame.Rect(0, 0, 0, 0)

    # ──────────────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ──────────────────────────────────────────────────────────────────────
    # Internals — event handling
    # ──────────────────────────────────────────────────────────────────────
    def _handle_events(self):
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Restart button (visible only when game_over)
                if self.game_over and self.restart_rect.collidepoint(mx, my):
                    self._restart()
                    return

                # Cell click (only when it's player's turn and game is live)
                if not self.game_over and self.player_turn:
                    cell = self._cell_at(mx, my)
                    if cell != -1 and self.board[cell] == " ":
                        self._place_piece(cell, "X")
                        if not self.game_over:
                            # Schedule computer move with short delay
                            self.player_turn    = False
                            self.computer_delay = time.time() + 0.55

        # Hover detection
        if not self.game_over and self.player_turn:
            self.hovered_cell = self._cell_at(mx, my)
            if self.hovered_cell != -1 and self.board[self.hovered_cell] != " ":
                self.hovered_cell = -1
        else:
            self.hovered_cell = -1

    # ──────────────────────────────────────────────────────────────────────
    # Internals — update
    # ──────────────────────────────────────────────────────────────────────
    def _update(self, dt):
        # Animate piece appearances
        for idx in list(self.pieces_anim):
            self.pieces_anim[idx] = min(1.0, self.pieces_anim[idx] + dt * 6)

        # Winner flash timer
        if self.winner_cells:
            self.flash_t += dt * 3.0

        # Computer move
        if (not self.player_turn and not self.game_over
                and time.time() >= self.computer_delay):
            self.computer_move()          # ← calls YOUR computer_move()
            move = next(
                (i for i, v in enumerate(self.board) if v == "O"
                 and i not in self.pieces_anim), -1
            )
            if move != -1:
                self.pieces_anim[move] = 0.0

            # Check result after computer moves
            if self.check_winner("O"):    # ← calls YOUR check_winner()
                self.winner_cells = self._find_winner_cells("O")
                self._end_game("LOSS")
            elif self.check_draw():       # ← calls YOUR check_draw()
                self._end_game("DRAW")
            else:
                self.player_turn = True

    # ──────────────────────────────────────────────────────────────────────
    # Internals — drawing
    # ──────────────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_grid()
        self._draw_pieces()
        self._draw_status_bar()
        if self.game_over:
            self._draw_popup()

    def _draw_header(self):
        surf = self.font_title.render("Tic Tac Toe", True, TEXT_MAIN)
        x = WIN_W // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, 10))

        name_surf = self.font_small.render(
            f"Player: {self.player_name}", True, TEXT_DIM
        )
        self.screen.blit(name_surf, (WIN_W // 2 - name_surf.get_width() // 2, 34))

    def _draw_grid(self):
        for row in range(3):
            for col in range(3):
                idx  = row * 3 + col
                rect = self._cell_rect(idx)

                # pick fill colour
                if idx in self.winner_cells:
                    pulse = 0.5 + 0.5 * math.sin(self.flash_t + idx)
                    fill  = self._lerp_color(CELL_ACTIVE, WIN_FLASH, pulse * 0.35)
                elif idx == self.hovered_cell:
                    fill = CELL_HOVER
                elif self.board[idx] != " ":
                    fill = CELL_ACTIVE
                else:
                    fill = CELL_IDLE

                self._draw_rounded_rect(self.screen, fill, rect, CORNER_R)

                # subtle border
                border_col = (55, 65, 105) if idx not in self.winner_cells else WIN_FLASH
                self._draw_rounded_rect_outline(self.screen, border_col, rect, CORNER_R, 2)

    def _draw_pieces(self):
        for idx, progress in self.pieces_anim.items():
            piece = self.board[idx]
            if piece == " ":
                continue
            rect  = self._cell_rect(idx)
            cx    = rect.centerx
            cy    = rect.centery
            scale = self._ease_out_back(progress)
            inset = int(PIECE_INSET + (1 - scale) * 40)

            if piece == "X":
                self._draw_x(cx, cy, rect.width - inset * 2, scale)
            else:
                self._draw_o(cx, cy, rect.width - inset * 2, scale)

    def _draw_x(self, cx, cy, size, scale):
        h = size // 2
        t = max(2, int(10 * scale))
        col = (*X_COLOR, int(255 * scale))
        surf = pygame.Surface((size + t * 2, size + t * 2), pygame.SRCALPHA)
        s = size + t * 2
        pygame.draw.line(surf, col, (t, t), (s - t, s - t), t)
        pygame.draw.line(surf, col, (s - t, t), (t, s - t), t)
        # round caps via circles
        for px, py in [(t, t), (s - t, s - t), (s - t, t), (t, s - t)]:
            pygame.draw.circle(surf, col, (px, py), t // 2)
        self.screen.blit(surf, (cx - s // 2, cy - s // 2))

    def _draw_o(self, cx, cy, size, scale):
        r     = int(size // 2 * scale)
        thick = max(2, int(10 * scale))
        if r <= thick:
            return
        # Glow layer
        glow_surf = pygame.Surface((r * 2 + 30, r * 2 + 30), pygame.SRCALPHA)
        gc = (*O_COLOR, 30)
        pygame.draw.circle(glow_surf, gc, (r + 15, r + 15), r + 6, thick + 6)
        self.screen.blit(glow_surf, (cx - r - 15, cy - r - 15))
        pygame.draw.circle(self.screen, O_COLOR, (cx, cy), r, thick)

    def _draw_status_bar(self):
        bar_y = WIN_H - 52
        if not self.game_over:
            if self.player_turn:
                msg = "Your turn  ·  click a cell"
                col = X_COLOR
            else:
                msg = "Computer is thinking…"
                col = O_COLOR
        else:
            msg = self.result_text
            col = WIN_FLASH

        surf = self.font_body.render(msg, True, col)
        self.screen.blit(surf, (WIN_W // 2 - surf.get_width() // 2, bar_y + 10))

    def _draw_popup(self):
        # Dim overlay
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 340, 200
        px     = WIN_W // 2 - pw // 2
        py     = WIN_H // 2 - ph // 2 - 20
        popup  = pygame.Rect(px, py, pw, ph)

        self._draw_rounded_rect(self.screen, POPUP_BG, popup, 18)
        self._draw_rounded_rect_outline(self.screen, POPUP_BORDER, popup, 18, 2)

        # Headline
        hl = self.font_popup.render(self.result_text, True, WIN_FLASH)
        self.screen.blit(hl, (WIN_W // 2 - hl.get_width() // 2, py + 28))

        # Sub-text
        sub = self.font_body.render("Game over", True, TEXT_DIM)
        self.screen.blit(sub, (WIN_W // 2 - sub.get_width() // 2, py + 78))

        # Restart button
        bw, bh = 160, 44
        bx     = WIN_W // 2 - bw // 2
        by     = py + ph - bh - 22
        self.restart_rect = pygame.Rect(bx, by, bw, bh)

        mx, my = pygame.mouse.get_pos()
        btn_col = BTN_HOVER if self.restart_rect.collidepoint(mx, my) else BTN_IDLE
        self._draw_rounded_rect(self.screen, btn_col, self.restart_rect, 10)

        btn_surf = self.font_body.render("Play Again", True, BTN_TEXT)
        self.screen.blit(
            btn_surf,
            (WIN_W // 2 - btn_surf.get_width() // 2, by + bh // 2 - btn_surf.get_height() // 2),
        )

    # ──────────────────────────────────────────────────────────────────────
    # Game logic hooks
    # ──────────────────────────────────────────────────────────────────────
    def _place_piece(self, cell_idx, piece):
        self.board[cell_idx] = piece
        self.pieces_anim[cell_idx] = 0.0

        if self.check_winner(piece):     # ← YOUR check_winner()
            self.winner_cells = self._find_winner_cells(piece)
            result = "WIN" if piece == "X" else "LOSS"
            self._end_game(result)
        elif self.check_draw():          # ← YOUR check_draw()
            self._end_game("DRAW")

    def _end_game(self, result):
        """
        Calls YOUR database functions, then shows the popup.
        ──────────────────────────────────────────────────────
        update_win / update_loss / update_draw / save_match
        are all wired here.
        """
        self.game_over = True

        if result == "WIN":
            self.result_text = "You Win! 🎉"
            self.update_win(self.player_name)     # ← YOUR update_win()
        elif result == "LOSS":
            self.result_text = "Computer Wins 💻"
            self.update_loss(self.player_name)    # ← YOUR update_loss()
        else:
            self.result_text = "It's a Draw 🤝"
            self.update_draw(self.player_name)    # ← YOUR update_draw()

        self.save_match(self.player_name, result) # ← YOUR save_match()

    def _restart(self):
        self.reset_board()               # ← YOUR reset_board()
        self.game_over     = False
        self.result_text   = ""
        self.winner_cells  = []
        self.player_turn   = True
        self.pieces_anim   = {}
        self.flash_t       = 0.0
        self.hovered_cell  = -1

    def _find_winner_cells(self, player):
        combos = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6],
        ]
        for combo in combos:
            if all(self.board[i] == player for i in combo):
                return combo
        return []

    # ──────────────────────────────────────────────────────────────────────
    # Geometry helpers
    # ──────────────────────────────────────────────────────────────────────
    def _cell_rect(self, idx):
        row = idx // 3
        col = idx  % 3
        gap = 6
        x   = GRID_MARGIN + col * (CELL_SIZE + gap)
        y   = GRID_TOP    + 55 + row * (CELL_SIZE + gap)   # +55 for header
        return pygame.Rect(x, y, CELL_SIZE - gap, CELL_SIZE - gap)

    def _cell_at(self, mx, my):
        for idx in range(9):
            if self._cell_rect(idx).collidepoint(mx, my):
                return idx
        return -1

    # ──────────────────────────────────────────────────────────────────────
    # Drawing utilities
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _draw_rounded_rect(surf, color, rect, radius):
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    @staticmethod
    def _draw_rounded_rect_outline(surf, color, rect, radius, width):
        pygame.draw.rect(surf, color, rect, width=width, border_radius=radius)

    @staticmethod
    def _lerp_color(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    @staticmethod
    def _ease_out_back(t):
        c1, c3 = 1.70158, 1.70158 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

    # ──────────────────────────────────────────────────────────────────────
    # Font initialisation
    # ──────────────────────────────────────────────────────────────────────
    def _init_fonts(self):
        candidates_title = ["Segoe UI", "SF Pro Display", "Helvetica Neue",
                            "Arial", "DejaVu Sans"]
        candidates_body  = ["Segoe UI", "SF Pro Text",    "Helvetica Neue",
                            "Arial", "DejaVu Sans"]
        self.font_title  = self._best_font(candidates_title, 26, bold=True)
        self.font_popup  = self._best_font(candidates_title, 28, bold=True)
        self.font_body   = self._best_font(candidates_body,  17)
        self.font_small  = self._best_font(candidates_body,  13)

    @staticmethod
    def _best_font(names, size, bold=False):
        for name in names:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.Font(None, size + 4)
