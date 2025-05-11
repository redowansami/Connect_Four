def create_board(rows=6, cols=7):
    return [[0 for _ in range(cols)] for _ in range(rows)]

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[len(board)-1][col] == 0

def get_next_open_row(board, col):
    for r in range(len(board)):
        if board[r][col] == 0:
            return r
    return -1

def winning_move(board, piece):
    rows = len(board)
    cols = len(board[0])
    
    for r in range(rows):
        for c in range(cols-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    
    for c in range(cols):
        for r in range(rows-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    
    for r in range(rows-3):
        for c in range(cols-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    
    for r in range(3, rows):
        for c in range(cols-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    
    return False