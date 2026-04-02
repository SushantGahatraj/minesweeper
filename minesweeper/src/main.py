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

class Tile: #Creating a Tile class
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x * size, y * size, size, size)
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

# Pick 15 random spots and turn 'is_mine' to True
all_spots = [(r, c) for r in range(ROWS) for c in range(COLS)]
for r, c in random.sample(all_spots, 15):
    grid[r][c].is_mine = True

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
                if tile.adjacent_mine == 0:
                    reveal_empty_tiles(grid,i,j)





while running:
    screen.fill((0, 0, 0)) # Clear screen with black
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Add your Right-Click Flagging logic here
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1. Get the pixel position of the click
            mouse_x, mouse_y = event.pos
            
            # 2. Convert pixels to Grid Coordinates (0 to 9)
            # If you click at x=85, 85 // 40 = Column 2
            c, r = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
            
            # 3. Get the specific Tile object from our 2D list
            tile = grid[r][c]

            if event.button == 1:  # Left Click
                    if not tile.is_flagged and not tile.is_revealed:
                        tile.is_revealed = True
                        
                        if tile.is_mine:
                            lives -= 1
                            print(f"BOOM! You hit a mine. Lives left: {lives}")
                            
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 1. Get the tile under the mouse
                mx, my = pygame.mouse.get_pos()
                c, r = mx // TILE_SIZE, my // TILE_SIZE
                
                # Safety check: make sure mouse is inside the grid
                if 0 <= r < ROWS and 0 <= c < COLS:
                    target_tile = grid[r][c]
                    
                    # 2. Only work if the player successfully FLAGGED a MINE
                    if target_tile.is_flagged and target_tile.is_mine:
                        print("Successful Detonation! Chain Reaction!")
                        
                        # 3. The 3x3 Loop: Reveal neighbors
                        for i in range(max(0, r-1), min(ROWS, r+2)):
                            for j in range(max(0, c-1), min(COLS, c+2)):
                                grid[i][j].is_revealed = True
                    
                    # 4. Penalty: If they detonated a wrong flag
                    elif target_tile.is_flagged and not target_tile.is_mine:
                        lives -= 1
                        print(f"Misfire! That wasn't a mine. Lives: {lives}")

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

