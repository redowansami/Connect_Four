
import pygame
from board import create_board, drop_piece, is_valid_location, get_next_open_row, winning_move
from minimaxAI import minimax


pygame.init()

ROWS = 6
COLS = 7
CELL_SIZE = 100
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE
RADIUS = int(CELL_SIZE / 2 - 5)
MAX_DEPTH = 4

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

def draw_board(screen, board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c*CELL_SIZE, r*CELL_SIZE+CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.circle(screen, BLACK, (c*CELL_SIZE+CELL_SIZE/2, r*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
    
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (c*CELL_SIZE+CELL_SIZE/2, (ROWS-r-1)*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (c*CELL_SIZE+CELL_SIZE/2, (ROWS-r-1)*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
    pygame.display.update()

def main():
    board = create_board()
    game_over = False
    turn = 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four/Connect Four")
    draw_board(screen, board)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, CELL_SIZE/2), RADIUS)
                pygame.display.update()
            
            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                col = posx // CELL_SIZE
                
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1)
                    
                    if winning_move(board, 1):
                        label = pygame.font.SysFont("monospace", 75).render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True
                    
                    turn = 1
                    draw_board(screen, board)
        
        if turn == 1 and not game_over:
            import time
            start_time = time.time()
            col, _ = minimax(board, MAX_DEPTH, -float('inf'), float('inf'), True, 2, start_time)
            
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)
                
                if winning_move(board, 2):
                    label = pygame.font.SysFont("monospace", 75).render("AI wins!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True
                
                turn = 0
                draw_board(screen, board)
        
        if game_over:
            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()
            return

if __name__ == "__main__":
    main()

