import pygame
from board import create_board, drop_piece, is_valid_location, get_next_open_row, winning_move
from minimaxAI import minimax

pygame.init()

ROWS = 6
COLS = 7
CELL_SIZE = 70  # Reduced from 80 to make board smaller
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE
RADIUS = int(CELL_SIZE / 2 - 5)

# Changed board color to wood-type brown
WOOD_BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
ASPARAGUS = (129, 159, 109)
PINK = (157, 17, 151)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

GRADIENT_TOP = (75, 0, 130)
GRADIENT_BOTTOM = (255, 105, 180)

# Initialize sound effects with proper error handling
drop_sound = win_sound = draw_sound = None
try:
    drop_sound = pygame.mixer.Sound("drop.wav")
    win_sound = pygame.mixer.Sound("win.wav")
    draw_sound = pygame.mixer.Sound("draw.wav")
    print("Sound files loaded successfully.")
except pygame.error as e:
    print(f"Error loading sound files: {e}. Sound effects disabled.")

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, text_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        try:
            self.font = pygame.font.Font("Game Paused DEMO.otf", 40)
        except pygame.error:
            self.font = pygame.font.SysFont("sans", 40)
            print("Custom font not found, using 'sans' fallback.")

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class TextInput:
    def __init__(self, x, y, width, height, prompt, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.prompt = prompt
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.submitted = False  # New flag to track if input is complete
        self.font = pygame.font.SysFont("sans", 30)
        self.color = GRAY
        self.active_color = WHITE
        self.submitted_color = DARK_GRAY  # Color for submitted input
        self.text_color = BLACK

    def handle_event(self, event):
        if self.submitted:
            return None  # Ignore events if input is already submitted
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN and self.text.strip():
                self.submitted = True
                self.active = False
                return self.text if self.text.strip() else "Player"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        return None

    def draw(self, screen):
        # Choose color based on state
        if self.submitted:
            pygame.draw.rect(screen, self.submitted_color, self.rect)
        elif self.active:
            pygame.draw.rect(screen, self.active_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        prompt_surf = self.font.render(self.prompt, True, self.text_color)
        text_surf = self.font.render(self.text, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(center=(self.rect.centerx, self.rect.top - 30))
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
        screen.blit(prompt_surf, prompt_rect)
        screen.blit(text_surf, text_rect)

def get_player_names(screen, game_mode, background_image):
    names = []
    prompts = ["Enter Player 1 Name:"] if game_mode == "ai_vs_player" else ["Enter Player 1 Name:", "Enter Player 2 Name:"]
    input_boxes = [TextInput((800 - 300) // 2, 300 + i * 100, 300, 40, prompt) for i, prompt in enumerate(prompts)]
    
    # Activate the first input box by default
    if input_boxes:
        input_boxes[0].active = True

    clock = pygame.time.Clock()  # To control frame rate

    while len(names) < len(prompts):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            for box in input_boxes:
                if not box.submitted:  # Only handle events for non-submitted boxes
                    result = box.handle_event(event)
                    if result:
                        names.append(result)
                        # Activate the next unsubmitted box, if any
                        for next_box in input_boxes:
                            if not next_box.submitted:
                                next_box.active = True
                                break

        # Draw the screen
        if background_image is not None:
            screen.blit(background_image, (0, 0))
        else:
            for y in range(600):
                r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / 600
                g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / 600
                b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / 600
                pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (800, y))
        
        try:
            title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
        except pygame.error:
            title_font = pygame.font.SysFont("sans", 60)
        title = title_font.render("Enter Player Names", True, WHITE)
        title_rect = title.get_rect(center=(800 // 2, 100))
        screen.blit(title, title_rect)
        
        # Draw all input boxes, regardless of submission state
        for box in input_boxes:
            box.draw(screen)
        
        pygame.display.flip()  # Update the entire screen once per frame
        clock.tick(60)  # Limit to 60 FPS to reduce CPU usage

    return names

def draw_board(screen, board):

    # Center the board
    board_x = (800 - WIDTH) // 2
    board_y = (600 - HEIGHT) // 2  # Adjust y to remove black row at top
    board_image = None
    try:
        board_image = pygame.image.load("board_image.jpg").convert()
        board_image = pygame.transform.scale(board_image, (WIDTH, HEIGHT-CELL_SIZE+20))
        screen.blit(board_image, (board_x, board_y))
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.circle(screen, BLACK, (board_x + c*CELL_SIZE+CELL_SIZE/2, board_y + r*CELL_SIZE+20+CELL_SIZE/2), RADIUS)
    except pygame.error as e:
        print(f"Error loading board image: {e}. Falling back to wood brown background.")
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(screen, WOOD_BROWN, (board_x + c*CELL_SIZE, board_y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.circle(screen, BLACK, (board_x + c*CELL_SIZE+CELL_SIZE/2, board_y + r*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
    
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1:
                pygame.draw.circle(screen, ASPARAGUS, (board_x + c*CELL_SIZE+CELL_SIZE/2, board_y + (ROWS-r-1)*CELL_SIZE+20+CELL_SIZE/2), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, PINK, (board_x + c*CELL_SIZE+CELL_SIZE/2, board_y + (ROWS-r-1)*CELL_SIZE+20+CELL_SIZE/2), RADIUS)
    pygame.display.update()

def draw_main_menu(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(600):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / 600
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / 600
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / 600
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (800, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Connect Four", True, WHITE)
    title_rect = title.get_rect(center=(800 // 2, 100))
    screen.blit(title, title_rect)
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def draw_choose_option(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(600):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / 600
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / 600
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / 600
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (800, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Choose Game Mode", True, WHITE)
    title_rect = title.get_rect(center=(800 // 2, 100))
    screen.blit(title, title_rect)
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def draw_difficulty_menu(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(600):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / 600
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / 600
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / 600
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (800, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Select Difficulty", True, WHITE)
    title_rect = title.get_rect(center=(800 // 2, 100))
    screen.blit(title, title_rect)
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def play_ai_vs_player(screen, depth, player_name):
    background_image = pygame.image.load("final_back.jpeg").convert()
    background_image = pygame.transform.scale(background_image, (800, 600))  # Maintain given proportion
    print("Background image loaded successfully.")
    if background_image is not None:
        screen.blit(background_image, (0, 0))

    board = create_board()
    game_over = False
    turn = 0
    draw_board(screen, board)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEMOTION and turn == 0:
                board_x = (800 - WIDTH) // 2
                pygame.draw.rect(screen, BLACK, (board_x, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                if board_x <= posx < board_x + WIDTH:
                    pygame.draw.circle(screen, ASPARAGUS, (posx, CELL_SIZE/2), RADIUS)
                pygame.display.update()
            
            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:
                board_x = (800 - WIDTH) // 2
                pygame.draw.rect(screen, BLACK, (board_x, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                if board_x <= posx < board_x + WIDTH:
                    col = (posx - board_x) // CELL_SIZE
                
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)
                        if drop_sound:
                            drop_sound.play()
                        
                        if winning_move(board, 1):
                            draw_board(screen, board)
                            try:
                                label = pygame.font.Font("Game Paused DEMO.otf", 75).render(f"{player_name} won!!", 1, ASPARAGUS)
                            except pygame.error:
                                label = pygame.font.SysFont("sans", 75).render(f"{player_name} won!!", 1, ASPARAGUS)
                            label_rect = label.get_rect(center=(800 // 2, 50))
                            bg_rect = label_rect.inflate(20, 20)
                            pygame.draw.rect(screen, BLACK, bg_rect)
                            screen.blit(label, label_rect)
                            pygame.display.update()
                            if win_sound:
                                win_sound.play()
                            pygame.time.wait(500)
                            game_over = True
                        
                        turn = 1
                        if not game_over:
                            draw_board(screen, board)
        
        if turn == 1 and not game_over:
            import time
            start_time = time.time()
            col, _ = minimax(board, depth, -float('inf'), float('inf'), True, 2, start_time, heuristic_type="original")
            
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)
                if drop_sound:
                    drop_sound.play()
                
                if winning_move(board, 2):
                    draw_board(screen, board)
                    try:
                        label = pygame.font.Font("Game Paused DEMO.otf", 70).render("AI wins!", 1, PINK)
                    except pygame.error:
                        label = pygame.font.SysFont("sans", 70).render("AI wins!", 1, PINK)
                    label_rect = label.get_rect(center=(800 // 2, 50))
                    bg_rect = label_rect.inflate(20, 20)
                    pygame.draw.rect(screen, BLACK, bg_rect)
                    screen.blit(label, label_rect)
                    pygame.display.update()
                    if win_sound:
                        win_sound.play()
                    pygame.time.wait(500)
                    game_over = True
                
                turn = 0
                if not game_over:
                    draw_board(screen, board)
        
        if game_over:
            pygame.time.wait(3000)
            return "main_menu"
