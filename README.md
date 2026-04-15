Detonator

Game Description
Detonator is a twist on the classic Minesweeper game built with Python and Pygame. 
The player uncovers a 10x10 grid hiding 15 mines, using logic and deduction to avoid explosions. Unlike classic Minesweeper, this version introduces a lives system, a chain reaction detonation mechanic, sound effects, and a persistent high score tracker.

The game starts when the player makes their first click, which is always guaranteed to be safe.
Mines are placed after the first click, ensuring no unfair instant losses. The timer begins on first click and stops when the game ends.

- How to Play
•	Left-click a tile to reveal it. Numbers show how many mines are adjacent.
•	If a revealed tile has no adjacent mines, surrounding tiles auto-reveal in a chain.
•	Right-click a tile to place or remove a flag to mark a suspected mine.
•	Hover over a suspected mine and press SPACE to safely detonate it and reveal the surrounding 3x3 area.
•	You start with 3 lives. Clicking a mine costs one life. Lose all lives and the game ends.
•	Win by correctly identifying (flagging or detonating) all 15 mines so none remain hidden.

- Key Features
•	Safe first click — mines are never placed under or adjacent to your first tile.
•	Chain detonation — SPACE reveals a 3x3 area around a correctly identified mine for bonus points.
•	Lives system — 3 lives let you survive accidental mine clicks before game over.
•	Score tracking — earn points for every safe tile revealed and every mine correctly detonated.
•	Persistent high score — your best score and fastest time are saved to highscore.txt between sessions.
•	Sound effects — distinct audio plays for mine hits and detonations.
•	Live header — displays Lives, Score, Timer, and Mines Left updated every frame.

- Controls

Key / Input	Action
Left Click	: Reveal a tile
Right Click	: Place or remove a flag on a hidden tile
SPACE	Detonate a mine : hover over it and press SPACE to safely reveal the 3x3 area around it
R :	Restart the game after game over or win
ESC :	Quit the game


OOP Logic
The game uses a Tile class as its core object-oriented component. Each tile on the 10x10 grid 
is an instance of this class, encapsulating all the state and rendering logic for a single cell.

Tile Class
Located in main.py, the Tile class is responsible for representing each cell on the minesweeper grid.

- Attributes:
•	row, col — the grid position of the tile (integers).
•	rect — a pygame.Rect object used for rendering and mouse collision detection.
•	is_mine — boolean, True if this tile contains a mine.
•	is_revealed — boolean, True if the tile has been uncovered by the player.
•	is_flagged — boolean, True if the player has right-clicked to flag the tile.
•	adjacent_mines — integer (0–8), the count of mines in the 8 surrounding tiles.

- Methods:
•	__init__(row, col, size) — initialises all attributes and computes the tile's pixel rectangle based on its grid position and tile size.
•	draw(surface) — renders the tile to the screen. Draws a dark background if revealed, light gray if hidden. Shows a red circle for mines, a cyan number for adjacent mine counts, and an orange square for flags. All visual logic is self-contained within this method.

The grid itself is a 2D list (list of lists) of Tile objects, built with a list comprehension:
grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]

This design keeps all per-tile state inside the object rather than scattered across multiple parallel arrays, making the code easier to read, debug, and extend.

- Supporting Functions
Outside the Tile class, the game logic is organised into focused helper functions:
•	place_mines(start_r, start_c) — randomly places mines after the first click, excluding the clicked tile and its neighbours to guarantee a safe start.
•	calculate_numbers() — iterates every tile and counts adjacent mines, populating the adjacent_mines attribute for each non-mine tile.
•	reveal_empty_tiles(r, c) — uses an iterative stack-based flood fill to auto-reveal all connected empty tiles when a zero-adjacent tile is clicked.
•	reveal_all_mines() — reveals every mine on the board, called when the game ends.
•	trigger_game_over() — sets the game over state and freezes the timer.
•	reset_game() — resets all global state variables and rebuilds the grid for a new game.
•	load_highscore() / save_highscore() — reads and writes the best score and time to highscore.txt for persistence between sessions.

- Tech Stack
•	Language: Python 3
•	Library: Pygame (rendering, input, audio)
•	Audio: pygame.mixer for .wav sound effects
•	Storage: Plain text file (highscore.txt) for persistent high score

- AI usage

#What AI Helped With

Recursive Logic: AI helped implement the stack-based "Flood Fill" algorithm for reveal_empty_tiles, 
preventing the game from crashing due to recursion depth limits when clearing large empty areas.

Header Responsiveness: I used AI to develop a dynamic font-scaling system for the header. 
This ensures the UI labels (Lives, Score, etc.) resize and space themselves correctly regardless of the window width.

Trigonometry & Coordinates: AI assisted in the math for get_tile_under_mouse, 
converting raw pixel coordinates from the Pygame window into specific row and column indices for the grid.

State Management: AI provided guidance on managing the transition 
between the active game loop and the "Game Over/Win" overlay states.

Code Documentation: Docstrings and internal comments were refined with AI to ensure professional clarity and maintainability.

# What I Figured Out Without AI

The Detonation Mechanic: The specific logic for the "Spacebar Detonation"—where a player is 
rewarded for "hunting" mines rather than just avoiding them—was a custom gameplay design choice I implemented manually.

Asset Integration: I manually handled the file pathing logic using os.path to ensure 
the game can find its sound files regardless of which folder it is launched from.


