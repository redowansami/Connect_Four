import math
import copy
import time

def evaluate_position(board, piece):
    score = 0
    opponent = 2 if piece == 1 else 1
    rows = len(board)
    cols = len(board[0])
    
    center_array = [board[r][cols//2] for r in range(rows)]
    center_count = center_array.count(piece)
    score += center_count * 3
    
    def score_window(window, piece):
        score = 0
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 4
        return score
    
    for r in range(rows):
        for c in range(cols-3):
            window = [board[r][c+i] for i in range(4)]
            score += score_window(window, piece)
    
    for c in range(cols):
        for r in range(rows-3):
            window = [board[r+i][c] for i in range(4)]
            score += score_window(window, piece)
    
    for r in range(rows-3):
        for c in range(cols-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, piece)
    
    for r in range(3, rows):
        for c in range(cols-3):
            window = [board[r-i][c+i] for i in range(4)]
            score += score_window(window, piece)
    
    return score

def get_valid_locations(board):
    return [col for col in range(len(board[0])) if board[len(board)-1][col] == 0]

def minimax(board, depth, alpha, beta, maximizingPlayer, piece, start_time, time_limit=2.0):
    valid_locations = get_valid_locations(board)
    is_terminal = len(valid_locations) == 0 or winning_move(board, 1) or winning_move(board, 2)
    
    if time.time() - start_time > time_limit:
        return None, evaluate_position(board, piece)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, piece):
                return None, 1000000
            elif winning_move(board, 2 if piece == 1 else 1):
                return None, -1000000
            else:
                return None, 0
        return None, evaluate_position(board, piece)
    
    if maximizingPlayer:
        value = -math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row == -1:
                continue
            board_copy = copy.deepcopy(board)
            drop_piece(board_copy, row, col, piece)
            _, new_score = minimax(board_copy, depth-1, alpha, beta, False, piece, start_time, time_limit)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row == -1:
                continue
            board_copy = copy.deepcopy(board)
            drop_piece(board_copy, row, col, 2 if piece == 1 else 1)
            _, new_score = minimax(board_copy, depth-1, alpha, beta, True, piece, start_time, time_limit)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

from board import winning_move, get_next_open_row, drop_piece