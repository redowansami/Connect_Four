
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

BLUE = (58, 44, 161)
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
        screen.blit(prompt_surf, (self.rect.x + 10, self.rect.y - 30))
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

def get_player_names(screen, game_mode, background_image):
    names = []
    prompts = ["Enter Player 1 Name:"] if game_mode == "ai_vs_player" else ["Enter Player 1 Name:", "Enter Player 2 Name:"]
    input_boxes = [TextInput((WIDTH - 300) // 2, 300 + i * 100, 300, 40, prompt) for i, prompt in enumerate(prompts)]
    
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
            for y in range(HEIGHT):
                r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / HEIGHT
                g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / HEIGHT
                b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / HEIGHT
                pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
        
        try:
            title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
        except pygame.error:
            title_font = pygame.font.SysFont("sans", 60)
        title = title_font.render("Enter Player Names", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw all input boxes, regardless of submission state
        for box in input_boxes:
            box.draw(screen)
        
        pygame.display.flip()  # Update the entire screen once per frame
        clock.tick(60)  # Limit to 60 FPS to reduce CPU usage

    return names

def draw_board(screen, board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c*CELL_SIZE, r*CELL_SIZE+CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.circle(screen, BLACK, (c*CELL_SIZE+CELL_SIZE/2, r*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
    
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1:
                pygame.draw.circle(screen, ASPARAGUS, (c*CELL_SIZE+CELL_SIZE/2, (ROWS-r-1)*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, PINK, (c*CELL_SIZE+CELL_SIZE/2, (ROWS-r-1)*CELL_SIZE+CELL_SIZE+CELL_SIZE/2), RADIUS)
    pygame.display.update()

def draw_main_menu(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(HEIGHT):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / HEIGHT
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / HEIGHT
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / HEIGHT
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Connect Four", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def draw_choose_option(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(HEIGHT):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / HEIGHT
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / HEIGHT
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / HEIGHT
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Choose Game Mode", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def draw_difficulty_menu(screen, buttons, background_image):
    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        for y in range(HEIGHT):
            r = GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / HEIGHT
            g = GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / HEIGHT
            b = GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / HEIGHT
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
    try:
        title_font = pygame.font.Font("Game Paused DEMO.otf", 60)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 60)
    title = title_font.render("Select Difficulty", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    for button in buttons:
        button.draw(screen)
    pygame.display.update()

def play_ai_vs_player(screen, depth, player_name):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(screen, board)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEMOTION and turn == 0:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, ASPARAGUS, (posx, CELL_SIZE/2), RADIUS)
                pygame.display.update()
            
            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                col = posx // CELL_SIZE
                
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
                        label_rect = label.get_rect(topright=(WIDTH - 20, 20))
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
                        label = pygame.font.Font("Game Paused DEMO.otf", 75).render("AI wins!", 1, PINK)
                    except pygame.error:
                        label = pygame.font.SysFont("sans", 75).render("AI wins!", 1, PINK)
                    label_rect = label.get_rect(topright=(WIDTH - 20, 20))
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

def play_playerA_vs_playerB(screen, player_names):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(screen, board)
    
    def is_board_full(board):
        for c in range(COLS):
            if is_valid_location(board, c):
                return False
        return True

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, ASPARAGUS, (posx, CELL_SIZE/2), RADIUS)
                else:
                    pygame.draw.circle(screen, PINK, (posx, CELL_SIZE/2), RADIUS)
                pygame.display.update()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, CELL_SIZE))
                posx = event.pos[0]
                col = posx // CELL_SIZE
                
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    player = turn + 1
                    drop_piece(board, row, col, player)
                    if drop_sound:
                        drop_sound.play()
                    
                    if winning_move(board, player):
                        draw_board(screen, board)
                        win_message = f"{player_names[player-1]} won!!"
                        print(f"Win detected for {player_names[player-1]}")
                        try:
                            label = pygame.font.Font("Game Paused DEMO.otf", 75).render(win_message, 1, ASPARAGUS if player == 1 else PINK)
                        except pygame.error:
                            label = pygame.font.SysFont("sans", 75).render(win_message, 1, ASPARAGUS if player == 1 else PINK)
                        label_rect = label.get_rect(topright=(WIDTH - 20, 20))
                        bg_rect = label_rect.inflate(20, 20)
                        pygame.draw.rect(screen, BLACK, bg_rect)
                        screen.blit(label, label_rect)
                        pygame.display.update()
                        if win_sound:
                            win_sound.play()
                        pygame.time.wait(500)
                        game_over = True
                        break
                    
                    elif is_board_full(board):
                        draw_board(screen, board)
                        print("Game ended in a draw")
                        try:
                            label = pygame.font.Font("Game Paused DEMO.otf", 75).render("Draw!", 1, WHITE)
                        except pygame.error:
                            label = pygame.font.SysFont("sans", 75).render("Draw!", 1, WHITE)
                        label_rect = label.get_rect(topright=(WIDTH - 20, 20))
                        bg_rect = label_rect.inflate(20, 20)
                        pygame.draw.rect(screen, BLACK, bg_rect)
                        screen.blit(label, label_rect)
                        pygame.display.update()
                        if draw_sound:
                            draw_sound.play()
                        pygame.time.wait(500)
                        game_over = True
                        break
                    
                    turn = 1 - turn
                    if not game_over:
                        draw_board(screen, board)
        
        if game_over:
            pygame.time.wait(3000)
            return "main_menu"

def play_ai_vs_ai(screen, depth):
    board = create_board()
    game_over = False
    turn = 0  # 0 for AI 1 (heuristic1), 1 for AI 2 (heuristic2)
    draw_board(screen, board)
    
    def is_board_full(board):
        for c in range(COLS):
            if is_valid_location(board, c):
                return False
        return True

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
        
        if not game_over:
            import time
            start_time = time.time()
            heuristic = "heuristic1" if turn == 0 else "heuristic2"
            piece = 1 if turn == 0 else 2
            col, _ = minimax(board, depth, -float('inf'), float('inf'), True, piece, start_time, heuristic_type=heuristic)
            
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, piece)
                if drop_sound:
                    drop_sound.play()
                draw_board(screen, board)
                pygame.time.wait(500)  # 500ms delay for visualization
                
                if winning_move(board, piece):
                    try:
                        label = pygame.font.Font("Game Paused DEMO.otf", 75).render(f"AI {piece} wins!", 1, ASPARAGUS if piece == 1 else PINK)
                    except pygame.error:
                        label = pygame.font.SysFont("sans", 75).render(f"AI {piece} wins!", 1, ASPARAGUS if piece == 1 else PINK)
                    label_rect = label.get_rect(topright=(WIDTH - 20, 20))
                    bg_rect = label_rect.inflate(20, 20)
                    pygame.draw.rect(screen, BLACK, bg_rect)
                    screen.blit(label, label_rect)
                    pygame.display.update()
                    if win_sound:
                        win_sound.play()
                    pygame.time.wait(500)
                    game_over = True
                
                elif is_board_full(board):
                    try:
                        label = pygame.font.Font("Game Paused DEMO.otf", 75).render("Draw!", 1, WHITE)
                    except pygame.error:
                        label = pygame.font.SysFont("sans", 75).render("Draw!", 1, WHITE)
                    label_rect = label.get_rect(topright=(WIDTH - 20, 20))
                    bg_rect = label_rect.inflate(20, 20)
                    pygame.draw.rect(screen, BLACK, bg_rect)
                    screen.blit(label, label_rect)
                    pygame.display.update()
                    if draw_sound:
                        draw_sound.play()
                    pygame.time.wait(500)
                    game_over = True
                
                turn = 1 - turn
        
        if game_over:
            pygame.time.wait(3000)
            return "main_menu"

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")
    
    background_image = None
    try:
        background_image = pygame.image.load("background.jpg").convert()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        print("Background image loaded successfully.")
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        background_image = None
        print("Falling back to gradient background.")
    
    start_button = Button("Start", (WIDTH - 200) // 2, 200, 200, 60, BLUE, GRAY, WHITE)
    choose_button = Button("Choose Option", (WIDTH - 300) // 2, 300, 300, 60, BLUE, GRAY, WHITE)
    quit_button = Button("Quit", (WIDTH - 200) // 2, 400, 200, 60, BLUE, GRAY, WHITE)
    main_menu_buttons = [start_button, choose_button, quit_button]
    
    ai_vs_player_button = Button("AI vs Player", (WIDTH - 300) // 2, 200, 300, 60, BLUE, GRAY, WHITE)
    playerA_vs_playerB_button = Button("Player vs Player", (WIDTH - 300) // 2, 300, 300, 60, BLUE, GRAY, WHITE)
    ai_vs_ai_button = Button("AI vs AI", (WIDTH - 300) // 2, 400, 300, 60, BLUE, GRAY, WHITE)
    choose_option_buttons = [ai_vs_player_button, playerA_vs_playerB_button, ai_vs_ai_button]
    
    easy_button = Button("Easy", (WIDTH - 200) // 2, 200, 200, 60, BLUE, GRAY, WHITE)
    medium_button = Button("Medium", (WIDTH - 200) // 2, 300, 200, 60, BLUE, GRAY, WHITE)
    hard_button = Button("Hard", (WIDTH - 200) // 2, 400, 200, 60, BLUE, GRAY, WHITE)
    difficulty_buttons = [easy_button, medium_button, hard_button]
    
    state = "main_menu"
    next_state = None
    selected_depth = 3  # Default depth
    player_names = None
    
    while True:
        if state == "main_menu":
            draw_main_menu(screen, main_menu_buttons, background_image)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if start_button.is_clicked(event):
                    state = "get_names"
                    next_state = "ai_vs_player"
                if choose_button.is_clicked(event):
                    state = "choose_option"
                if quit_button.is_clicked(event):
                    pygame.quit()
                    return
        
        elif state == "choose_option":
            draw_choose_option(screen, choose_option_buttons, background_image)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if ai_vs_player_button.is_clicked(event):
                    state = "get_names"
                    next_state = "ai_vs_player"
                if playerA_vs_playerB_button.is_clicked(event):
                    state = "get_names"
                    next_state = "player_vs_player"
                if ai_vs_ai_button.is_clicked(event):
                    state = "difficulty"
                    next_state = "ai_vs_ai"
        
        elif state == "get_names":
            player_names = get_player_names(screen, next_state, background_image)
            if player_names is None:
                state = "quit"
            else:
                state = "difficulty" if next_state in ["ai_vs_player", "ai_vs_ai"] else play_playerA_vs_playerB(screen, player_names)
        
        elif state == "difficulty":
            draw_difficulty_menu(screen, difficulty_buttons, background_image)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if easy_button.is_clicked(event):
                    selected_depth = 1
                    if next_state == "ai_vs_player":
                        state = play_ai_vs_player(screen, selected_depth, player_names[0])
                    elif next_state == "ai_vs_ai":
                        state = play_ai_vs_ai(screen, selected_depth)
                if medium_button.is_clicked(event):
                    selected_depth = 4
                    if next_state == "ai_vs_player":
                        state = play_ai_vs_player(screen, selected_depth, player_names[0])
                    elif next_state == "ai_vs_ai":
                        state = play_ai_vs_ai(screen, selected_depth)
                if hard_button.is_clicked(event):
                    selected_depth = 6
                    if next_state == "ai_vs_player":
                        state = play_ai_vs_player(screen, selected_depth, player_names[0])
                    elif next_state == "ai_vs_ai":
                        state = play_ai_vs_ai(screen, selected_depth)
        
        elif state == "quit":
            pygame.quit()
            return

if __name__ == "__main__":
    main()