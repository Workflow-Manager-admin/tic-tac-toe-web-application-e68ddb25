from enum import Enum
from typing import List, Optional, Tuple

class Player(str, Enum):
    X = 'X'
    O = 'O'

class GameStatus(str, Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    DRAW = 'DRAW'
    WINNER_X = 'WINNER_X'
    WINNER_O = 'WINNER_O'

# PUBLIC_INTERFACE
def initial_board() -> List[List[Optional[str]]]:
    """Returns a new empty Tic Tac Toe board (3x3 grid)."""
    return [[None for _ in range(3)] for _ in range(3)]

# PUBLIC_INTERFACE
def get_next_player(board: List[List[Optional[str]]]) -> Player:
    """Returns the player who should play next based on current board."""
    x_count = sum(cell == Player.X for row in board for cell in row)
    o_count = sum(cell == Player.O for row in board for cell in row)
    return Player.O if x_count > o_count else Player.X

# PUBLIC_INTERFACE
def check_winner(board: List[List[Optional[str]]]) -> Optional[Player]:
    """Check the board for a winner and return Player.X or Player.O, or None."""
    lines = (
        # Rows
        [(i, j) for j in range(3)] for i in range(3)
    )
    cols = (
        [(j, i) for j in range(3)] for i in range(3)
    )
    diags = [
        [(i, i) for i in range(3)],
        [(i, 2 - i) for i in range(3)]
    ]
    for line_indices in list(lines) + list(cols) + diags:
        for line in [line_indices]:
            line_marks = [board[i][j] for i, j in line]
            if line_marks[0] and all(cell == line_marks[0] for cell in line_marks):
                if line_marks[0] == Player.X:
                    return Player.X
                elif line_marks[0] == Player.O:
                    return Player.O
    return None

# PUBLIC_INTERFACE
def is_draw(board: List[List[Optional[str]]]) -> bool:
    """Returns True if all cells are filled and there is no winner."""
    if any(cell is None for row in board for cell in row):
        return False
    return check_winner(board) is None

# PUBLIC_INTERFACE
def get_game_status(board: List[List[Optional[str]]]) -> GameStatus:
    """Returns the current status of the game."""
    winner = check_winner(board)
    if winner == Player.X:
        return GameStatus.WINNER_X
    elif winner == Player.O:
        return GameStatus.WINNER_O
    elif is_draw(board):
        return GameStatus.DRAW
    else:
        return GameStatus.IN_PROGRESS

# PUBLIC_INTERFACE
def play_move(
    board: List[List[Optional[str]]], 
    row: int, 
    col: int, 
    player: Player
    ) -> Tuple[List[List[Optional[str]]], Optional[str]]:
    """
    Attempt to play a move on the board.

    Returns:
        (updated_board, error_message), error_message is None on success.
    """
    if row < 0 or row > 2 or col < 0 or col > 2:
        return board, "Move out of bounds."
    if board[row][col] is not None:
        return board, "Cell already taken."
    expected_player = get_next_player(board)
    if player != expected_player:
        return board, f"It's {expected_player}'s turn."
    next_board = [r.copy() for r in board]
    next_board[row][col] = player
    return next_board, None
