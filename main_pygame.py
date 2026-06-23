"""
main_pygame.py — Entry point for the Pygame Tic Tac Toe
========================================================
This file is the ONLY file you need to modify to connect
your existing logic.  Everything else is wired via the
TicTacToeUI constructor.

HOW IT CONNECTS TO YOUR ORIGINAL CODE
───────────────────────────────────────
  ✅ board            → shared list used by all your functions
  ✅ reset_board()    → called on "Play Again"
  ✅ check_winner()   → called after every human & computer move
  ✅ check_draw()     → called after every human & computer move
  ✅ computer_move()  → called by the UI after a short delay
  ✅ update_win()     → called via _end_game("WIN")
  ✅ update_loss()    → called via _end_game("LOSS")
  ✅ update_draw()    → called via _end_game("DRAW")
  ✅ save_match()     → called via _end_game(result)
  ✅ add_player()     → called at startup (unchanged)

  ✗ play_game()      → replaced by the UI event loop
                        (all its logic is replicated cell-by-cell in pygame_ui.py)
  ✗ print_board()    → not needed (Pygame draws the board)
  ✗ show_positions() → not needed (board is clickable)
  ✗ player_move()    → not needed (mouse click handles this)
  ✗ show_stats() / show_leaderboard() / show_match_history()
                      → still available; call them from a terminal
                        or add extra Pygame screens later.

STRUCTURE
─────────
  main_pygame.py    ← YOU ARE HERE (entry point + wiring)
  pygame_ui.py      ← Pygame rendering & input (do not edit for logic)
  main.py           ← Your original CLI game (untouched)
  database.py       ← Your original DB layer  (untouched)
"""

# ── 1. Import your original game logic (unchanged) ─────────────────────────
from main import (       # <── your original main.py
    board,
    reset_board,
    check_winner,
    check_draw,
    computer_move,
)

from database import (   # <── your original database.py
    add_player,
    save_match,
    update_win,
    update_loss,
    update_draw,
)

# ── 2. Import the Pygame UI layer ───────────────────────────────────────────
from pygame_ui import TicTacToeUI


# ── 3. Get player name & register in DB ────────────────────────────────────
def main():
    print("=" * 40)
    print("  Tic Tac Toe — Pygame Edition")
    print("=" * 40)
    player_name = input("Enter your name: ").strip() or "Player"

    add_player(player_name)   # ← YOUR add_player(), unchanged

    # ── 4. Build UI, passing all your functions as callbacks ───────────────
    ui = TicTacToeUI(
        player_name      = player_name,
        board            = board,            # shared mutable list

        # ── logic callbacks (your original functions) ──────────────────────
        check_winner_fn  = check_winner,
        check_draw_fn    = check_draw,
        computer_move_fn = computer_move,
        update_win_fn    = update_win,
        update_loss_fn   = update_loss,
        update_draw_fn   = update_draw,
        save_match_fn    = save_match,
        reset_board_fn   = reset_board,
    )

    # ── 5. Start the game loop ─────────────────────────────────────────────
    ui.run()


if __name__ == "__main__":
    main()
