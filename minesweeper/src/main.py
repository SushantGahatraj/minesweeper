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

#Initalize Stats
score = 0
lives = START_LIVES
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
        # 1. Background Color (Hidden = Gray, Revealed = Black)
        if not self.is_revealed:
            color = (180, 180, 180) 
        else:
            color = (20, 20, 20)    
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 1) # Thin dark border

        # 2. Show contents ONLY if revealed
        if self.is_revealed:
            if self.is_mine:
                # Clean Red Mine (No diagonal line)
                pygame.draw.circle(surface, (255, 0, 0), self.rect.center, 15)
            elif self.adjacent_mines > 0:
                # Show numbers (Only if greater than 0)
                font = pygame.font.SysFont('Arial', 24, bold=True)
                text = font.render(str(self.adjacent_mines), True, (0, 255, 255))
                # Centering the text slightly
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
            # If adjacent_mines is 0, it does nothing (stays blank black)

        # 3. Flags (Orange for visibility)
        elif self.is_flagged:
            flag_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, 20, 20)
            pygame.draw.rect(surface, (255, 165, 0), flag_rect)
# Game Settings
ROWS, COLS = 10, 10
TILE_SIZE = 40
grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]



first_click = True
running = True

def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def calculate_numbers():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c].is_mine:
                continue
            # Check all 8 neighbors
            count = 0
            for i in range(max(0, r-1), min(ROWS, r+2)):
                for j in range(max(0, c-1), min(COLS, c+2)):
                    if grid[i][j].is_mine:
                        count += 1
            grid[r][c].adjacent_mines = count

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
       calculate_numbers(grid)
     
def trigger_game_over():
    global game_over, end_ticks
    for row in grid:
        for t in row:
            if t in row:
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
                            place_mines(grid, r, c) 
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
                    target_tile = grid[r][c]
                    
                    # 3. SUCCESS: Detonate correctly flagged mines
                    if target_tile.is_flagged and target_tile.is_mine:
                        print("Successful Detonation! Chain Reaction!")
                        score += 50  # Add a points bonus from the Final Code
                        
                        # The 3x3 Loop: Reveal every neighbor safely
                        for i in range(max(0, r-1), min(ROWS, r+2)):
                            for j in range(max(0, c-1), min(COLS, c+2)):
                                if not grid[i][j].is_revealed:
                                    grid[i][j].is_revealed = True
                                    score += 10 # Extra points for chain reveals
                        
                        # Remove the flag after detonation
                        target_tile.is_flagged = False

                    # 4. PENALTY: Detonating a fake flag
                    elif target_tile.is_flagged and not target_tile.is_mine:
                        lives -= 1
                        print(f"Misfire! Lives: {lives}")

    # Draw the grid
    for row in grid:
        for tile in row:
            tile.draw(screen)
    font = pygame.font.SysFont('Arial', 24, bold=True)
    life_text = font.render(f"LIVES: {lives}", True, (255, 0, 0))
    # Position it at the top left (or wherever fits your screen)
    screen.blit(life_text, (10, 10))

    pygame.draw.rect(screen, (0,0,0), (0,0, SCREEN_WIDTH, HEADER_HEIGHT)) # Clear header area with black

    elapsed = 0
    if start_ticks:
        if game_over and end_ticks:
            elapsed = (end_ticks - start_ticks) // 1000
        else:
            elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    mines_left = count_mines_remaining()

    font = pygame.font.SysFont("Arial", 18, bold=True)
    stats_str = f"LIVES: {lives}  SCORE: {score}  TIME:elapsed {elapsed}s"
    text_surf = font.render(stats_str, True, (255, 255, 255))
    screen.blit(text_surf, (10, (HEADER_HEIGHT - text_surf.get_height()) // 2)) # Center text vertically in header


    pygame.display.flip()

pygame.quit()

