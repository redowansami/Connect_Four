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
    
    def score_window(window, player):
        score = 0
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(0) == 2:
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

def evaluate_heuristic1(board, piece, opponent):
    score = 0
    rows = len(board)
    cols = len(board[0])

    def is_square_available(board, r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if board[r][c] != 0:
            return False
        
        if r > 0 and board[r-1][c] == 0:
            return False
        return True

    def check_window(window, player, r_start, c_start, direction):
        score = 0
        if window.count(player) == 4:
            return float('inf')
        elif window.count(player) == 3 and window.count(0) == 1:
            if direction == 'horizontal':
                c = c_start + window.index(0)
                if is_square_available(board, r_start, c-1) or is_square_available(board, r_start, c+4):
                    return float('inf')
                elif is_square_available(board, r_start, c):
                    return 900000
            elif direction == 'vertical':
                r = r_start + window.index(0)
                if is_square_available(board, r, c_start):
                    return 900000
            elif direction == 'diagonal_pos':
                r = r_start + window.index(0)
                c = c_start + window.index(0)
                if is_square_available(board, r, c):
                    return 900000
            elif direction == 'diagonal_neg':
                r = r_start - window.index(0)
                c = c_start + window.index(0)
                if is_square_available(board, r, c):
                    return 900000
            return 0
        elif window.count(player) == 2 and window.count(0) == 2:
            if direction == 'horizontal':
                c1 = c_start + window.index(0)
                c2 = c_start + window.index(0, window.index(0)+1)
                if is_square_available(board, r_start, c1-1) or is_square_available(board, r_start, c2+1):
                    return 50000
                elif is_square_available(board, r_start, c1) or is_square_available(board, r_start, c2):
                    return window.count(0) * 4 
                return 0
            elif direction == 'vertical':
                r1 = r_start + window.index(0)
                r2 = r_start + window.index(0, window.index(0)+1)
                if is_square_available(board, r1, c_start) or is_square_available(board, r2, c_start):
                    return window.count(0) * 4
                return 0
            elif direction == 'diagonal_pos':
                r1 = r_start + window.index(0)
                c1 = c_start + window.index(0)
                r2 = r_start + window.index(0, window.index(0)+1)
                c2 = c_start + window.index(0, window.index(0)+1)
                if is_square_available(board, r1, c1) or is_square_available(board, r2, c2):
                    return window.count(0) * 4
                return 0
            elif direction == 'diagonal_neg':
                r1 = r_start - window.index(0)
                c1 = c_start + window.index(0)
                r2 = r_start - window.index(0, window.index(0)+1)
                c2 = c_start + window.index(0, window.index(0)+1)
                if is_square_available(board, r1, c1) or is_square_available(board, r2, c2):
                    return window.count(0) * 4
                return 0
        return 0

    for r in range(rows):
        for c in range(cols - 3):
            window = [board[r][c + i] for i in range(4)]
            if window.count(piece) > 0 and window.count(opponent) == 0:
                score += check_window(window, piece, r, c, 'horizontal')
            elif window.count(opponent) > 0 and window.count(piece) == 0:
                score -= check_window(window, opponent, r, c, 'horizontal')

    for c in range(cols):
        for r in range(rows - 3):
            window = [board[r + i][c] for i in range(4)]
            if window.count(piece) > 0 and window.count(opponent) == 0:
                score += check_window(window, piece, r, c, 'vertical')
            elif window.count(opponent) > 0 and window.count(piece) == 0:
                score -= check_window(window, opponent, r, c, 'vertical')

    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r + i][c + i] for i in range(4)]
            if window.count(piece) > 0 and window.count(opponent) == 0:
                score += check_window(window, piece, r, c, 'diagonal_pos')
            elif window.count(opponent) > 0 and window.count(piece) == 0:
                score -= check_window(window, opponent, r, c, 'diagonal_pos')

    for r in range(3, rows):
        for c in range(cols - 3):
            window = [board[r - i][c + i] for i in range(4)]
            if window.count(piece) > 0 and window.count(opponent) == 0:
                score += check_window(window, piece, r, c, 'diagonal_neg')
            elif window.count(opponent) > 0 and window.count(piece) == 0:
                score -= check_window(window, opponent, r, c, 'diagonal_neg')

    for r in range(rows - 3):
        for c in range(cols - 3):
            if r + 2 < rows and c + 2 < cols:
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    score += 900000
                elif board[r][c] == opponent and board[r+1][c+1] == opponent and board[r+2][c+2] == opponent and board[r+3][c+3] == opponent:
                    score -= 900000
    for r in range(3, rows):
        for c in range(cols - 3):
            if r - 2 >= 0 and c + 2 < cols:
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    score += 900000
                elif board[r][c] == opponent and board[r-1][c+1] == opponent and board[r-2][c+2] == opponent and board[r-3][c+3] == opponent:
                    score -= 900000

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == piece:
                if c == 3:  
                    score += 200
                elif c in [2, 4]: 
                    score += 120
                elif c in [1, 5]: 
                    score += 70
                elif c in [0, 6]: 
                    score += 40
            elif board[r][c] == opponent:
                if c == 3:
                    score -= 200
                elif c in [2, 4]:
                    score -= 120
                elif c in [1, 5]:
                    score -= 70
                elif c in [0, 6]:
                    score -= 40

    return score

def evaluate_heuristic2(board, piece, opponent):
    score = 0
    rows = len(board)
    cols = len(board[0])
    value_matrix = [
        [3, 4, 5, 7, 5, 4, 3],
        [4, 6, 8, 10, 8, 6, 4],
        [5, 8, 11, 13, 11, 8, 5],
        [5, 8, 11, 13, 11, 8, 5],
        [4, 6, 8, 10, 8, 6, 4],
        [3, 4, 5, 7, 5, 4, 3]
    ]

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == piece:
                score += value_matrix[r][c]
            elif board[r][c] == opponent:
                score -= value_matrix[r][c]

    return score

def get_valid_locations(board):
    return [col for col in range(len(board[0])) if board[len(board)-1][col] == 0]

def minimax(board, depth, alpha, beta, maximizingPlayer, piece, start_time, time_limit=2.0, heuristic_type="original"):
    valid_locations = get_valid_locations(board)
    is_terminal = len(valid_locations) == 0 or winning_move(board, 1) or winning_move(board, 2)
    
    if time.time() - start_time > time_limit:
        if heuristic_type == "heuristic1":
            return None, evaluate_heuristic1(board, piece, 2 if piece == 1 else 1)
        elif heuristic_type == "heuristic2":
            return None, evaluate_heuristic2(board, piece, 2 if piece == 1 else 1)
        else:
            return None, evaluate_position(board, piece)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, piece):
                return None, 1000000
            elif winning_move(board, 2 if piece == 1 else 1):
                return None, -1000000
            else:
                return None, 0
        if heuristic_type == "heuristic1":
            return None, evaluate_heuristic1(board, piece, 2 if piece == 1 else 1)
        elif heuristic_type == "heuristic2":
            return None, evaluate_heuristic2(board, piece, 2 if piece == 1 else 1)
        else:
            return None, evaluate_position(board, piece)
    
    if maximizingPlayer:
        value = -math.inf
        column = valid_locations[0] if valid_locations else None
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row == -1:
                continue
            board_copy = copy.deepcopy(board)
            drop_piece(board_copy, row, col, piece)
            _, new_score = minimax(board_copy, depth-1, alpha, beta, False, piece, start_time, time_limit, heuristic_type)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = valid_locations[0] if valid_locations else None
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row == -1:
                continue
            board_copy = copy.deepcopy(board)
            drop_piece(board_copy, row, col, 2 if piece == 1 else 1)
            _, new_score = minimax(board_copy, depth-1, alpha, beta, True, piece, start_time, time_limit, heuristic_type)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

from board import winning_move, get_next_open_row, drop_piece