import pygame
import os
import random

# Mandatory path handling from project instructions 
GAME_PATH = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(GAME_PATH, "assets", filename)

# Initialize Pygame
pygame.init()
SCREEN_SIZE = 400
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Chain Reaction Minesweeper")

#Game Settings
ROWS, COLS = 10,10
TITLE_SIZE = 40
HEADER_HEIGHT = 50
SCREEN_WIDTH = COLS * TITLE_SIZE
SCREEN_HEIGHT = ROWS * TITLE_SIZE + HEADER_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chain Reaction Minesweeper")
clock = pygame.time.Clock()

#Initalize Stats
score = 0
lives = 3
start_ticks = pygame.time.get_ticks()

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
grid = [[Tile(c, r, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]
lives = 3 # Your specific twist rule


first_click = True
running = True

def calculate_numbers(grid):
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

def reveal_empty_tiles(grid, r,c):
    '''Reveals the surrounding tiles automatically if the current one is empty (0).'''
    #1. Loop through all 8 neighbors
    for i in range(max(0,r-1),min(ROWS, r+2)):
        for j in range(max(0,c-1), min(COLS, c+2)):
            tile = grid[i][j]
            #2. Only reveal if it's not a mine, not flagged, and not already revealed
            if not tile.is_mine and not tile.is_flagged and not tile.is_revealed:
                tile.is_revealed = True
                #3. RECURSION : If this neighbour is ALSO empty (0), check its neighbors too!
                if tile.adjacent_mines == 0:
                    reveal_empty_tiles(grid,i,j)

def place_mines(grid, start_r, start_c):
    possible_spots = [(r,c) for r in range(ROWS) for c in range(COLS) if (r,c) != (start_r, start_c)]
    for r, c in random.sample(possible_spots, 15):
        grid[r][c].is_mine = True
        calculate_numbers(grid)


while running:
    screen.fill((0, 0, 0)) # Clear screen with black
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Add your Right-Click Flagging logic here
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            c = mx // TITLE_SIZE
            r = (my - HEADER_HEIGHT) // TITLE_SIZE #udjusting the mouse postiion to account for header height

            if event.button == 1:  # Left Click
                    if not tile.is_flagged and not tile.is_revealed:
                        #First click should never be mine
                        if first_click:
                            place_mines(grid, r, c) 
                            first_click = False

                        tile.is_revealed = True
                        
                        if tile.is_mine:
                            lives -= 1
                            print(f"BOOM! You hit a mine. Lives left: {lives}")

                        elif tile.adjacent_mines == 0:
                            #If the tile is empty, start the chain reaction!
                            reveal_empty_tiles(grid,r,c)

                    
                        if lives <= 0:
                            print("GAME OVER! You ran out of lives.")
                                # REVEAL ALL MINES so the player sees where they were
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
                c = mx // TILE_SIZE  # Ensure this is TILE_SIZE, not TITLE_SIZE
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
    pygame.display.flip()

pygame.quit()

