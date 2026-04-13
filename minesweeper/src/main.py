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
pygame.display.set_caption("Chain Reaction Minesweeper")
clock = pygame.time.Clock()

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


#Initalize Stats
score = 0
lives = START_LIVES
first_click = True
start_ticks = None # Will be set on first click to start the timer
end_ticks = None #used to stop timer on game over
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
     
def trigger_game_over():
    global game_over, end_ticks
    for row in grid:
        for t in row:
                if t.is_mine:
                    t.is_revealed = True
    game_over = True
    if end_ticks is None and start_ticks is not None:
        end_ticks = pygame.time.get_ticks()            


def count_mines_remaining():
    return sum(1 for row in grid for t in row if t.is_mine and not (t.is_revealed or t.is_flagged))

def reset_game():
    global grid, score, lives, start_ticks, end_ticks, game_over, first_click
    grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]
    score = 0
    lives = START_LIVES
    start_ticks = None
    end_ticks = None
    game_over = False
    first_click = True

while running:
    screen.fill((0, 0, 0)) # Clear screen with black
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
            continue  # Skip the rest of the loop if game is over
        
        # Add your Right-Click Flagging logic here
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            c = mx // TILE_SIZE
            r = (my - HEADER_HEIGHT) // TILE_SIZE #udjusting the mouse postiion to account for header height

            if 0 <= r < ROWS and 0 <= c < COLS:
                tile = grid[r][c]
            else:
                continue

            if event.button == 1:  # Left Click
                    if not tile.is_flagged and not tile.is_revealed:
                        #First click should never be mine
                        if first_click:
                            place_mines(r, c) 
                            first_click = False
                            start_ticks = pygame.time.get_ticks()


                        tile.is_revealed = True
                        
                        if tile.is_mine:
                            lives -= 1
                            print(f"BOOM! You hit a mine. Lives left: {lives}")
                            if lives <= 0:
                                trigger_game_over()

                        else:
                            score += 1 # +1 for every safe reveal
                            if tile.adjacent_mines == 0:
                                reveal_empty_tiles(r, c)

                    
                        if lives <= 0:
                         game_over = True
                        end_ticks = pygame.time.get_ticks()

                        for row in grid:
                            for t in row:
                                if t.is_mine:
                                    t.is_revealed = True


            
            elif event.button == 3: # Right Click (FLAG)
                if not tile.is_revealed:
                    tile.is_flagged = not tile.is_flagged

            # Adding Spacebar Detonation logic here
            # --- STEP 4: DETONATION LOGIC ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 1. Get mouse position and subtract the header
                mx, my = pygame.mouse.get_pos()
                c = mx // TILE_SIZE  
                r = (my - HEADER_HEIGHT) // TILE_SIZE 
                
                # 2. Check if we are inside the grid
                if 0 <= r < ROWS and 0 <= c < COLS:
                    tile = grid[r][c]
                    
                    # 3. SUCCESS: Detonate correctly flagged mines
                if tile.is_mine and not tile.is_revealed:
                    score += 1   # +1 for the mine itself
                    for i in range(r - 1, r + 2):
                        for j in range(c - 1, c + 2):
                            if in_bounds(i, j):
                                t = grid[i][j]
                                if not t.is_revealed and not t.is_mine:
                                    score += 1
                                    t.is_revealed = True
                                    t.is_flagged  = False
                    tile.is_flagged  = False
                    tile.is_revealed = True   # reveal the mine too
                else:
                    if first_click:   # mines not placed yet — ignore
                        continue
                    lives -= 1
                    if tile.is_flagged:
                        tile.is_flagged = False
                    if lives <= 0:
                        trigger_game_over()
                    
    # Draw the grid
    for row in grid:
        for tile in row:
            tile.draw(screen)
    pygame.draw.rect(screen, COLOR_HEADER_BG, (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
    
    elapsed = 0
    if start_ticks:
        if game_over and end_ticks:
            elapsed = (end_ticks - start_ticks) // 1000
        else:
            elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    mines_left = count_mines_remaining()

    header_labels = [
        f"LIVES: {lives}",
        f"SCORE: {score}",
        f"TIMER: {elapsed}s",        # fixed label
        f"MINES LEFT: {mines_left}",
    ]

   

# 3. Adaptive font sizing:
chosen_surfaces = None
chosen_gap = 5
for size in [16, 14, 12]:
    f = pygame.font.SysFont("Arial", size, bold=True)
    surfs = [f.render(t, True, COLOR_HEADER_TEXT)
             for t in header_labels]
    total_w = sum(s.get_width() for s in surfs)
    gap = (SCREEN_WIDTH - 20 - total_w) / 3
    if gap >= 8:
        chosen_surfaces, chosen_gap = surfs, gap
        break
if chosen_surfaces is None:
    f = pygame.font.SysFont("Arial", 12, bold=True)
    chosen_surfaces = [f.render(t, True, COLOR_HEADER_TEXT)
                       for t in header_labels]
    tw = sum(s.get_width() for s in chosen_surfaces)
    chosen_gap = max(0, SCREEN_WIDTH - 20 - tw) / 3

x = 10
for surf in chosen_surfaces:
    screen.blit(surf,
        (x, (HEADER_HEIGHT - surf.get_height()) // 2))
    x += surf.get_width() + chosen_gap


    pygame.display.flip()

pygame.quit()

