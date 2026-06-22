import random
from database import (
    add_player,
    save_match,
    update_win,
    update_loss,
    update_draw,
    show_stats,
    show_leaderboard,
    show_match_history
)
# Create Board
board = [" " for _ in range(9)]


# Reset Board
def reset_board():
    global board
    board = [" " for _ in range(9)]


# Display Board
def print_board():
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()


# Position Guide
def show_positions():
    print("\nPosition Guide")
    print(" 1 | 2 | 3 ")
    print("---+---+---")
    print(" 4 | 5 | 6 ")
    print("---+---+---")
    print(" 7 | 8 | 9 ")
    print()


# Check Winner
def check_winner(player):
    winning_combinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ]

    for combo in winning_combinations:
        if all(board[pos] == player for pos in combo):
            return True

    return False


# Check Draw
def check_draw():
    return " " not in board


# Player Move
def player_move():
    while True:
        try:
            move = int(input("Choose position (1-9): ")) - 1

            if move < 0 or move > 8:
                print("❌ Invalid position! Choose between 1 and 9.")
                continue

            if board[move] == " ":
                board[move] = "X"
                break
            else:
                print("⚠️ Position already occupied!")

        except ValueError:
            print("❌ Please enter a valid number.")


# Computer Move
def computer_move():
    available_moves = [i for i in range(9) if board[i] == " "]

    move = random.choice(available_moves)

    print(f"💻 Computer chose position {move + 1}")

    board[move] = "O"


# Main Game Logic
def play_game(player_name):

    show_positions()

    while True:

        print_board()

        # Player Turn
        player_move()

        if check_winner("X"):
            print_board()
            print("🎉 Congratulations! You Win!")

            update_win(player_name)
            save_match(player_name, "WIN")

            break

        if check_draw():
            print_board()
            print("🤝 It's a Draw!")

            update_draw(player_name)
            save_match(player_name, "DRAW")

            break

        # Computer Turn
        computer_move()

        if check_winner("O"):
            print_board()
            print("💻 Computer Wins!")

            update_loss(player_name)
            save_match(player_name, "LOSS")

            break

        if check_draw():
            print_board()
            print("🤝 It's a Draw!")

            update_draw(player_name)
            save_match(player_name, "DRAW")

            break


# ==========================
# Main Program
# ==========================

# ==========================
# Main Program
# ==========================

player_name = input("Enter your name: ")
add_player(player_name)

while True:

    print("\n===== MENU =====")
    print("1. Play Game")
    print("2. View Stats")
    print("3. View Leaderboard")
    print("4. View Match History")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":

        reset_board()
        play_game(player_name)

    elif choice == "2":

        show_stats(player_name)

    elif choice == "3":

        show_leaderboard()

    elif choice == "4":

        show_match_history()

    elif choice == "5":

        print("\n👋 Thanks for playing!")
        break

    else:

        print("❌ Invalid Choice!")