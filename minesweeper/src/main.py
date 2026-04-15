import pygame
import os
import random
import sys

#Game Settings
ROWS, COLS = 10,10
TILE_SIZE = 40
HEADER_HEIGHT = 50
SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE + HEADER_HEIGHT
MINE_COUNT = 15
START_LIVES = 3

# Mandatory path handling from project instructions 
GAME_PATH = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(GAME_PATH, "assets", filename)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Detonator Minesweeper")
clock = pygame.time.Clock()

pygame.mixer.init()
sound_mine_hit = pygame.mixer.Sound(get_asset_path("mine_hit.wav"))
sound_detonate = pygame.mixer.Sound(get_asset_path("mine_detonate.wav"))
sound_reveal_single = pygame.mixer.Sound(get_asset_path("reveal_single.wav"))
sound_reveal_chain = pygame.mixer.Sound(get_asset_path("reveal_chain.wav"))

#Colors and fonts
COLOR_HIDDEN = (180, 180, 180)
COLOR_REVEALED = (20, 20, 20)
COLOR_BORDER = (80, 80, 80)
COLOR_MINE = (255, 0, 0)
COLOR_FLAG = (255, 165, 0)
COLOR_NUMBER = (0, 255, 255)
COLOR_HEADER_BG = (0, 0, 0)
COLOR_HEADER_TEXT = (255, 255, 255)
FONT = pygame.font.SysFont("Arial", 12, bold=True)
NUMBER_FONT = pygame.font.SysFont("Arial", 24, bold=True)
GAME_OVER_FONT = pygame.font.SysFont("Arial", 48, bold=True)


#Initalize Stats
score = 0
lives = START_LIVES
first_click = True
start_ticks = None # Will be set on first click to start the timer
end_ticks = None #used to stop timer on game over
game_won = False #tracks if player won
game_over = False #tracks if game ended


class Tile: #Creating a Tile class
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(col * size, (row * size) + HEADER_HEIGHT, size, size)
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

    def draw(self, surface):
        # Base color: Hidden or Revealed
        color = COLOR_REVEALED if self.is_revealed else COLOR_HIDDEN 
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 1) # Thin dark border

        
        if self.is_revealed:
            if self.is_mine:
                # Clean Red Mine (No diagonal line)
                pygame.draw.circle(surface, COLOR_MINE, self.rect.center, TILE_SIZE // 3)

            elif self.adjacent_mines > 0:
                text = NUMBER_FONT.render(str(self.adjacent_mines), True, COLOR_NUMBER)
                surface.blit(text, text.get_rect(center=self.rect.center))

        
        else:
            #flag shown only on hidden tiles
            if self.is_flagged:
                flag_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, TILE_SIZE - 20, TILE_SIZE - 20)
                pygame.draw.rect(surface, COLOR_FLAG, flag_rect)

#Building the board as a 2D list of Tile objects
grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]

def in_bounds(r, c):
    '''Returns True if the given row and column are within the grid bounds.'''
    return 0 <= r < ROWS and 0 <= c < COLS

def calculate_numbers():
    for r in range(ROWS):
        for c in range(COLS):
            tile = grid[r][c]
            if tile.is_mine:
                tile.adjacent_mines = 0
                continue
            # Check all 8 neighbors
            count = 0
            for i in range(r - 1, r + 2):
                for j in range(c - 1, c + 2):
                    if in_bounds(i,j) and grid[i][j].is_mine:
                        count += 1
            tile.adjacent_mines = count

def reveal_empty_tiles(r,c):
    stack = [(r,c)]
    visited = set()

    while stack:    
        cr, cc = stack.pop()
        if (cr, cc) in visited:
            continue
        visited.add((cr, cc))
        tile = grid[cr][cc]

        if tile.is_mine or tile.is_flagged:
            continue

        if not tile.is_revealed:
            tile.is_revealed = True

        if tile.adjacent_mines == 0:
            for i in range(cr - 1, cr + 2):
                for j in range(cc - 1, cc + 2):
                    if in_bounds(i,j) and (i,j) not in visited:
                        stack.append((i, j))
               

def place_mines(start_r, start_c):
    excluded = {(start_r, start_c)}
    for i in range(start_r - 1, start_r + 2):
       for j in range(start_c - 1, start_c + 2):
           if in_bounds(i, j):
               excluded.add((i, j))

    possible = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in excluded]
    mine_count = min(MINE_COUNT, len(possible))
    max_attempts = 100
    for attempt in range(max_attempts):
       # clear any previous mines
       for r in range(ROWS):
           for c in range(COLS):
               grid[r][c].is_mine = False

       random.shuffle(possible)
       placed = 0
       for r, c in possible:
           if placed >= mine_count:
               break
           # check adjacency: skip if any neighbor already has a mine
           ok = True
           for i in range(r - 1, r + 2):
               for j in range(c - 1, c + 2):
                      if in_bounds(i, j) and grid[i][j].is_mine:
                       ok = False
                       break
               if not ok:
                   break
           if not ok:
               continue
           grid[r][c].is_mine = True
           placed += 1


       if placed >= mine_count:
           break
    calculate_numbers()

def reveal_all_mines():
    '''Reveals all mines on the grid. Used for game over.'''
    for row in grid:
        for t in row:
                if t.is_mine:
                    t.is_revealed = True

     
def trigger_game_over():
    '''Handles game over state: reveals all mines and stops the timer.'''
    global game_over, end_ticks
    reveal_all_mines()
    game_over = True
    if end_ticks is None and start_ticks is not None:
        end_ticks = pygame.time.get_ticks()            



def reset_game():
    global grid, score, lives, start_ticks, end_ticks, game_over, first_click, game_won, best_score, best_time
    grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]
    score = 0
    lives = START_LIVES
    first_click = True
    start_ticks = None
    end_ticks = None
    game_over = False
    game_won = False
    best_score, best_time = load_highscore()
    
    #Rebuild the grid
    grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]
    
def get_tile_under_mouse(mx, my):
    '''Returns the tile under the given mouse coordinates, or None if out of bounds.'''
    col = mx // TILE_SIZE
    row = (my - HEADER_HEIGHT) // TILE_SIZE
    if in_bounds(row, col):
        return grid[row][col] , row, col
    return None, None, None

def count_flagged():
    #Count how many tiles the player has flagged.
    return sum(1 for row in grid for t in row if t.is_flagged)

def count_total_mines():
    #Return the total number of mines actually places on the board.
    return sum(1 for row in grid for t in row if t.is_mine)

def count_mines_remaining():
    #Calculate how many mines are left based on total mines and flagged tiles.
    return sum(
        1 for row in grid for t in row
        if t.is_mine and not (t.is_revealed or t.is_flagged)
    )
HIGHSCORE_PATH = os.path.join(GAME_PATH, "highscore.txt")

def load_highscore():
    try:
        with open(HIGHSCORE_PATH, "r") as f:
            parts = f.read().strip().split(",")
            return int(parts[0]), int(parts[1])
    except:
        return 0, 999

def save_highscore(score, time):
    with open(HIGHSCORE_PATH, "w") as f:
        f.write(f"{score},{time}")

best_score, best_time = load_highscore()

chosen_surfaces = None
chosen_font = FONT
chosen_gap = 5

#Main Loop
running = True
while running:
    clock.tick(60) # Limit to 60 FPS
    screen.fill((60, 60, 60)) # Clear screen with dark gray
    
    #Draw header background
    pygame.draw.rect(screen, COLOR_HEADER_BG, (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

    #Timer (freeze when game over using end_ticks)
    elapsed = 0
    if start_ticks:
        end_time = end_ticks if end_ticks is not None else pygame.time.get_ticks()
        elapsed = (end_time - start_ticks) // 1000
    
    #Show how many mines remains unidentified (not revealed and not flagged)

    mines_left = sum(1 for row in grid for t in row if t.is_mine and not t.is_revealed)

    #Header labels with dynamic mine count and timer
    header_labels = [
        f"LIVES: {lives}",
        f"SCORE: {score}",
        f"TIMER: {elapsed}s",
        f"MINES LEFT: {mines_left}"
    ]
    candidate_sizes = [16, 14, 12]  
    chosen_gap = 5
    for size in candidate_sizes:
        f = pygame.font.SysFont("Arial", size, bold=True)
        surfs = [f.render(txt, True, COLOR_HEADER_TEXT) for txt in header_labels]
        total_w = sum(s.get_width() for s in surfs)
        total_space = SCREEN_WIDTH - 20 - total_w # 20 pixels total padding (10 on each side)
        gaps = 3
        gap = total_space / gaps if gaps > 0 else 0
        if gap >= 8:
            chosen_font = f
            chosen_surfaces = surfs
            chosen_gap = gap
            break

         # If no large size fit, use the smallest candidate with computed surfaces
    if chosen_surfaces is None:
        f = pygame.font.SysFont("Arial", candidate_sizes[-1], bold=True)
        chosen_font = f
        chosen_surfaces = [f.render(txt, True, COLOR_HEADER_TEXT) for txt in header_labels]
        total_w = sum(s.get_width() for s in chosen_surfaces)
        total_space = max(0, SCREEN_WIDTH - 20 - total_w)
        chosen_gap = total_space / 3 if total_space > 0 else 5

    # Position items with equal gap starting at 10px
    x = 10
    for surf in chosen_surfaces:
        screen.blit(surf, (x, (HEADER_HEIGHT - surf.get_height()) // 2))
        x += surf.get_width() + chosen_gap    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                   running = False
            continue  # Skip the rest of the loop if game is over
        
        # Add your Right-Click Flagging logic here
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            tile, r, c = get_tile_under_mouse(mx, my)
            if tile is None:
                continue

            if event.button == 1:  # Left Click
                    if tile.is_flagged or tile.is_revealed:
                        continue
                        #First click should never be mine
                    if first_click:
                        place_mines(r, c) 
                        first_click = False
                        start_ticks = pygame.time.get_ticks()
                    tile.is_revealed = True
                    
                    if tile.is_mine:
                        lives -= 1
                        sound_mine_hit.play()
                        print(f"BOOM! You hit a mine. Lives left: {lives}")
                        if lives <= 0:
                            trigger_game_over()

                    else:
                        score += 1
                        if tile.adjacent_mines == 0:
                            sound_reveal_chain.play()
                            reveal_empty_tiles(r, c)
                        else:
                            sound_reveal_single.play()

           
            elif event.button == 3: # Right Click (FLAG)
                if not tile.is_revealed:
                    tile.is_flagged = not tile.is_flagged


            # Adding Spacebar Detonation logic here            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mx, my = pygame.mouse.get_pos()
                tile, r, c = get_tile_under_mouse(mx, my)
                if tile is None:
                    continue

               # If the tile under the cursor is a mine, allow a safe detonation
               # whether or not it's flagged. This reveals the 3x3 (including
               # the targeted tile) without penalizing the player.
               # Only allow detonation if the mine is still hidden. If the
               # mine has already been revealed (player clicked it earlier),
               # pressing SPACE should do nothing.

                if tile.is_mine and not tile.is_revealed:
                    #Award an extra point for correctly identifying a mine with SPACE, even if it wasn't flagged  
                    score += 1
                    sound_detonate.play()
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if in_bounds(i, j):
                                t = grid[i][j]
                                if not t.is_revealed and not t.is_mine:
                                    score += 1
                                t.is_revealed = True
                                t.is_flagged  = False
                    #ensure the detonated mine itself is revealed and unflagged
                    tile.is_flagged  = False                  
                else:
                    if first_click:   # mines not placed yet — ignore
                        continue
                    lives -= 1
                    if tile.is_flagged:
                        tile.is_flagged = False
                    if lives <= 0:
                        trigger_game_over()
        
        
        #Allow restart or quit when game is over
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q or event.type == pygame.K_ESCAPE:
                    running = False     

    # Win condition check
    if not game_over and not first_click:
        unrevealed_safe = sum(
            1 for row in grid for t in row
            if not t.is_mine and not t.is_revealed
    )
        if unrevealed_safe == 0:
            game_won = True
            game_over = True
            if end_ticks is None and start_ticks is not None:
                end_ticks = pygame.time.get_ticks()        

    # Draw the grid
    for row in grid:
        for tile in row:
            tile.draw(screen)

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        small_font = pygame.font.SysFont("Arial", 20)

        if game_won:
            title_text = GAME_OVER_FONT.render("YOU WIN!", True, (0, 255, 0))
        else:
            title_text = GAME_OVER_FONT.render("GAME OVER", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(title_text, title_rect)

        final_time = (end_ticks - start_ticks) // 1000 if end_ticks and start_ticks else 0
        summary_text = small_font.render(f"Score: {score}  |  Time: {final_time}s", True, (255, 255, 255))
        summary_rect = summary_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(summary_text, summary_rect)

        if score >= best_score and game_won:
            best_text = small_font.render("New Best!  🏆", True, (255, 215, 0))
            best_rect = best_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(best_text, best_rect)

        restart_text = small_font.render("Press R to Restart  |  ESC to Quit", True, (180, 180, 180))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

pygame.quit()

sys.exit()
