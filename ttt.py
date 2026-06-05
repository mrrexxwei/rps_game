"""
tic_tac_toe_with_difficulty.py

Tic-Tac-Toe with three difficulty levels and a pre-game popup to choose difficulty.
- Easy   : random moves
- Medium : tries to win or block, otherwise random
- Hard   : unbeatable Minimax AI

This script will also try to load a PNG icon if present at:
  /mnt/data/A_black_and_white_line_drawing_of_a_butterfly_is_d.png
(That path was provided in the session and will be used as a window icon if available.)

Run:
    python tic_tac_toe_with_difficulty.py
"""

import tkinter as tk
from tkinter import messagebox
import random
import os

# --- Optional icon file provided in the session (will be used if exists) ---
DEFAULT_ICON_PATH = "/mnt/data/A_black_and_white_line_drawing_of_a_butterfly_is_d.png"

# --- Game constants ---
PLAYER = "X"
AI = "O"
EMPTY = ""
GRID_SIZE = 3

# Global state (will be initialized in main)
board = None
buttons = None
root = None
difficulty = "Medium"  # default if popup fails


# -------------------------
# Game logic functions
# -------------------------
def check_win(bd):
    """Return 'X' or 'O' if a player has won, 'Tie' if full with no winner, or None otherwise."""
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6)              # diags
    ]
    for a, b, c in wins:
        if bd[a] == bd[b] == bd[c] != EMPTY:
            return bd[a]
    if EMPTY not in bd:
        return "Tie"
    return None


def empty_indices(bd):
    return [i for i, v in enumerate(bd) if v == EMPTY]


# -------------------------
# AI: Easy (random)
# -------------------------
def ai_easy_move(bd):
    empties = empty_indices(bd)
    if not empties:
        return None
    return random.choice(empties)


# -------------------------
# AI: Medium (win/block/random)
# -------------------------
def find_winning_move(bd, symbol):
    """Return index of winning move for symbol, or None."""
    for i in empty_indices(bd):
        bd_copy = bd[:]
        bd_copy[i] = symbol
        if check_win(bd_copy) == symbol:
            return i
    return None


def ai_medium_move(bd):
    # 1) Win if possible
    move = find_winning_move(bd, AI)
    if move is not None:
        return move
    # 2) Block player's win
    move = find_winning_move(bd, PLAYER)
    if move is not None:
        return move
    # 3) Otherwise random
    return ai_easy_move(bd)


# -------------------------
# AI: Hard (Minimax)
# -------------------------
def minimax(bd, is_maximizing):
    result = check_win(bd)
    if result == AI:
        return 1
    elif result == PLAYER:
        return -1
    elif result == "Tie":
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for i in empty_indices(bd):
            bd[i] = AI
            score = minimax(bd, False)
            bd[i] = EMPTY
            if score > best_score:
                best_score = score
        return best_score
    else:
        best_score = float("inf")
        for i in empty_indices(bd):
            bd[i] = PLAYER
            score = minimax(bd, True)
            bd[i] = EMPTY
            if score < best_score:
                best_score = score
        return best_score


def ai_hard_move(bd):
    best_score = -float("inf")
    best_move = None
    for i in empty_indices(bd):
        bd[i] = AI
        score = minimax(bd, False)
        bd[i] = EMPTY
        if score > best_score:
            best_score = score
            best_move = i
    # fallback
    if best_move is None:
        return ai_easy_move(bd)
    return best_move


# -------------------------
# UI & Interaction
# -------------------------
def perform_ai_move():
    global board
    move = None
    if difficulty == "Easy":
        move = ai_easy_move(board)
    elif difficulty == "Medium":
        move = ai_medium_move(board)
    else:  # Hard
        move = ai_hard_move(board)

    if move is not None:
        place_symbol(move, AI)


def place_symbol(index, symbol):
    """Place symbol on board and update UI; handle endgame or switch to AI."""
    global board
    if board[index] != EMPTY:
        return

    board[index] = symbol
    buttons[index].config(text=symbol, state="disabled", disabledforeground="black")

    winner = check_win(board)
    if winner:
        handle_game_over(winner)
        return

    # If player just played and game not over, trigger AI (if player was X)
    if symbol == PLAYER:
        # small delay so UI updates nicely
        root.after(200, perform_ai_move)


def handle_game_over(winner):
    global board
    if winner == "Tie":
        messagebox.showinfo("Game Over", "It's a tie!")
    else:
        messagebox.showinfo("Game Over", f"Player {winner} wins!")
    reset_game()


def on_button_click(i):
    # Player click handling (player always X)
    if board[i] == EMPTY:
        place_symbol(i, PLAYER)


def reset_game():
    global board, buttons
    board = [EMPTY] * 9
    for btn in buttons:
        btn.config(text="", state="normal")


# -------------------------
# Difficulty selection popup (Option C)
# -------------------------
def open_difficulty_popup():
    """Show a modal popup before the game starts to choose difficulty."""
    popup = tk.Toplevel(root)
    popup.title("Choose Difficulty")
    popup.grab_set()  # Make modal

    tk.Label(popup, text="Choose difficulty:", font=("Arial", 12)).pack(padx=12, pady=(10, 6))

    var = tk.StringVar(value="Medium")

    def on_start():
        nonlocal var
        global difficulty
        difficulty = var.get()
        popup.grab_release()
        popup.destroy()

    # Radio buttons
    frame = tk.Frame(popup)
    frame.pack(padx=12, pady=6)
    tk.Radiobutton(frame, text="Easy (Random moves)", variable=var, value="Easy").pack(anchor="w")
    tk.Radiobutton(frame, text="Medium (Win/Block heuristic)", variable=var, value="Medium").pack(anchor="w")
    tk.Radiobutton(frame, text="Hard (Unbeatable Minimax)", variable=var, value="Hard").pack(anchor="w")

    start_btn = tk.Button(popup, text="Start Game", command=on_start)
    start_btn.pack(pady=(6, 12))

    # Center popup over root
    root.update_idletasks()
    popup.update_idletasks()
    popup.geometry(f"+{root.winfo_x() + 50}+{root.winfo_y() + 50}")

    popup.wait_window()  # Wait until closed


# -------------------------
# Building the main Tkinter UI
# -------------------------
def build_ui():
    global root, buttons
    root.title("Tic-Tac-Toe with Difficulty")
    # Try to set icon if provided
    try:
        if os.path.exists(DEFAULT_ICON_PATH):
            img = tk.PhotoImage(file=DEFAULT_ICON_PATH)
            root.iconphoto(False, img)
    except Exception:
        pass  # ignore if icon can't be loaded

    # Grid of buttons
    btn_font = ("Arial", 36)
    buttons = []
    for i in range(9):
        b = tk.Button(root, text="", font=btn_font, width=4, height=2,
                      command=lambda i=i: on_button_click(i))
        b.grid(row=i // GRID_SIZE, column=i % GRID_SIZE, padx=2, pady=2)
        buttons.append(b)

    # Reset button and difficulty info
    ctrl_frame = tk.Frame(root)
    ctrl_frame.grid(row=GRID_SIZE, column=0, columnspan=GRID_SIZE, pady=(8, 4))
    reset_btn = tk.Button(ctrl_frame, text="Reset", width=10, command=reset_game)
    reset_btn.pack(side="left", padx=6)
    # Show current difficulty
    diff_label = tk.Label(ctrl_frame, text="Difficulty: " + difficulty)
    diff_label.pack(side="left", padx=6)

    # A small note label
    note = tk.Label(root, text="You are X. Click an empty cell to play. Computer is O.", font=("Arial", 10))
    note.grid(row=GRID_SIZE + 1, column=0, columnspan=GRID_SIZE, pady=(0, 8))


# -------------------------
# Main entrypoint
# -------------------------
def main():
    global board, root, difficulty
    board = [EMPTY] * 9
    root = tk.Tk()

    # First show difficulty popup (Option C)
    # Build minimal UI first to get a parent window position, then popup
    root.withdraw()  # hide while we position
    root.geometry("300x350")  # temporary size so popup centers nicely
    root.deiconify()
    root.update_idletasks()

    open_difficulty_popup()  # sets global difficulty

    # Build full UI now that difficulty chosen
    build_ui()

    # Update difficulty label (since it was built after popup)
    # find label in control frame and update text
    for widget in root.grid_slaves(row=GRID_SIZE, column=0):
        # the control frame is at that grid position
        ctrl_frame = widget
        for child in ctrl_frame.winfo_children():
            if isinstance(child, tk.Label) and child.cget("text").startswith("Difficulty:"):
                child.config(text="Difficulty: " + difficulty)

    root.mainloop()


if __name__ == "__main__":
    main()


# ===================  project 02 ===================
# import tkinter as tk
# from tkinter import messagebox
# import random

# root = tk.Tk()
# root.title("Tic-Tac-Toe AI")

# PLAYER = "X"
# AI = "O"
# board = [""] * 9
# buttons = []


# def check_win():
#     win_conditions = [
#         (0,1,2), (3,4,5), (6,7,8),
#         (0,3,6), (1,4,7), (2,5,8),
#         (0,4,8), (2,4,6)
#     ]
#     for a, b, c in win_conditions:
#         if board[a] == board[b] == board[c] != "":
#             return board[a]
#     return None


# def ai_move():
#     """Simple AI: picks a random empty spot."""
#     empty_indexes = [i for i, v in enumerate(board) if v == ""]
#     if not empty_indexes:
#         return

#     choice = random.choice(empty_indexes)
#     board[choice] = AI
#     buttons[choice].config(text=AI)

#     winner = check_win()
#     if winner:
#         messagebox.showinfo("Game Over", f"Player {winner} wins!")
#         reset_game()
#         return

#     if "" not in board:
#         messagebox.showinfo("Game Over", "It's a tie!")
#         reset_game()
#         return


# def on_click(i):
#     if board[i] != "":  
#         return

#     board[i] = PLAYER
#     buttons[i].config(text=PLAYER)

#     winner = check_win()
#     if winner:
#         messagebox.showinfo("Game Over", f"Player {winner} wins!")
#         reset_game()
#         return

#     if "" not in board:
#         messagebox.showinfo("Game Over", "It's a tie!")
#         reset_game()
#         return

#     root.after(300, ai_move)   # AI moves after short delay


# def reset_game():
#     global board
#     board = [""] * 9
#     for btn in buttons:
#         btn.config(text="")
    

# # UI layout
# for i in range(9):
#     btn = tk.Button(root, text="", font=("Arial", 32),
#                     width=5, height=2,
#                     command=lambda i=i: on_click(i))
#     btn.grid(row=i//3, column=i%3)
#     buttons.append(btn)

# reset_btn = tk.Button(root, text="Reset", font=("Arial", 16),
#                       command=reset_game)
# reset_btn.grid(row=3, column=0, columnspan=3, sticky="WE")

# root.mainloop()

# ===================  project 01 ===================
# import tkinter as tk
# from tkinter import messagebox

# # Create main window
# root = tk.Tk()
# root.title("Tic-Tac-Toe")

# current_player = "X"
# board = [""] * 9   # Flat list for 3x3 grid


# def check_win():
#     win_conditions = [
#         (0,1,2), (3,4,5), (6,7,8),  # rows
#         (0,3,6), (1,4,7), (2,5,8),  # columns
#         (0,4,8), (2,4,6)            # diagonals
#     ]

#     for a, b, c in win_conditions:
#         if board[a] == board[b] == board[c] != "":
#             return board[a]
#     return None


# def on_click(i):
#     global current_player

#     if board[i] != "":  
#         return  # ignore clicks on filled cells

#     board[i] = current_player
#     buttons[i].config(text=current_player)

#     winner = check_win()
#     if winner:
#         messagebox.showinfo("Game Over", f"Player {winner} wins!")
#         reset_game()
#         return

#     if "" not in board:
#         messagebox.showinfo("Game Over", "It's a tie!")
#         reset_game()
#         return

#     current_player = "O" if current_player == "X" else "X"


# def reset_game():
#     global board, current_player
#     board = [""] * 9
#     current_player = "X"
#     for btn in buttons:
#         btn.config(text="")


# # Create buttons grid
# buttons = []
# for i in range(9):
#     btn = tk.Button(root, text="", font=("Arial", 30), width=5, height=2,
#                     command=lambda i=i: on_click(i))
#     btn.grid(row=i//3, column=i%3)
#     buttons.append(btn)

# # Reset button
# reset_btn = tk.Button(root, text="Reset", font=("Arial", 16),
#                       command=reset_game)
# reset_btn.grid(row=3, column=0, columnspan=3, sticky="WE")

# root.mainloop()
