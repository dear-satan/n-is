# N-is: A Generalized Tetris Game

N-is is a terminal-based puzzle game that generalizes the classic Tetris concept to work with polyominos of any size from 1 to 6 blocks. Play traditional Tetris (4 blocks) or experiment with Tris (3 blocks), Dis (2 blocks), Pentis (5 blocks), or even Hexis (6 blocks)!

<figure>
    <img src="./example.png">
    <figcaption>Example game of tetris with extended mode enabled.</figcaption>
</figure>

## Features

- **Flexible Block Size**: Choose your game style with different block counts:
  - **1**: "Monois" (single blocks)
  - **2**: "Dis" (domino shapes) 
  - **3**: "Tris" (triomino shapes)
  - **4**: "Tetris" (classic tetromino shapes)
  - **5**: "Pentis" (pentomino shapes - more challenging)
  - **6**: "Hexis" (hexomino shapes - extremely challenging, nearly unplayable)

  Heptis will probably never be made because even hexis is not very fun, and heptis just simply has no reason to exist.

- **Interactive Menu System**: Run without arguments to access a user-friendly curses-based menu for selecting game options

- **Extended Mode**: Enable with `-e` flag to add non-standard polyominos (polykings) that can connect at vertices

- **Mix Mode**: Enable with `-m` flag to include polyominos of lower order (e.g., in Tetris mode, also get Tris and Dis pieces)

- **Advanced Gameplay Features**:
  - **Hold System**: Hold pieces for later use with 'c' key
  - **Ghost Piece**: See where your piece will land
  - **Hard Drop**: Instantly drop pieces with Enter key
  - **Combo System**: Chain line clears for bonus points

- **Customizable Appearance**: 
  - Choose block and background colors with `-c` and `-bc` flags
  - Change colors during gameplay with j/k and u/i

- **Progressive Difficulty**: 
  - Fall speed increases with each level
  - Scoring system with level and combo multipliers

## Installation & Usage

### Prerequisites

- Python 3.x
- Standard Python libraries: `curses`, `random`, `argparse`, `math`
- Terminal with adequate size
- `polyshapes.py` file in the same directory

### Running the Game

#### Interactive Mode (Recommended)

Simply run the game without arguments to access the interactive menu:

```bash
python n-is.py
```

Navigate the menu with:
- **Arrow keys**: Navigate options
- **Enter**: Select option
- **Number keys (1-6)**: Quick select
- **Q**: Quit menu

#### Command Line Mode

For direct game launch:

```bash
python n-is.py <N> [OPTIONS]
```

**Arguments:**
- `N` (optional): Number of blocks (1-6). If omitted, interactive menu appears
- `-e`: Enable extended mode (polykings/pseudo-polyominos)
- `-m`: Enable mix mode (include lower-order polyominos)
- `-c COLOR`: Block color (`r`, `g`, `b`, `y`, `m`, `c`, `w` or 0-255)
- `-bc NUMBER`: Background color (0-255)
- `-h`: Show help message

**Examples:**
```bash
python n-is.py              # Interactive menu
python n-is.py 4            # Classic Tetris
python n-is.py 3 -e         # Tris with polykings
python n-is.py 5 -c g -bc 0 # Green Pentis on black background
python n-is.py 4 -m         # Tetris with Tris and Dis pieces included
```

### Alternative Installation

You can also compile the game into an executable:

```bash
pyinstaller n-is.py
```

The executable will be available in the `dist/` directory.

## Game Controls

### Movement & Rotation
- **Left/Right Arrow**: Move piece horizontally
- **Down Arrow**: Soft drop (faster fall + 1 point per cell)
- **Up Arrow**: Rotate piece clockwise
- **Enter**: Hard drop (instant drop + 2 points per cell)

### Game Features
- **C**: Hold current piece (swap with held piece)
- **Q**: Quit game

### Visual Customization (During Game)
- **U/I**: Change main block color (previous/next)
- **J/K**: Change background color (previous/next)

## Game Mechanics

### Scoring System
- **Line Clears**: Points based on number of lines cleared simultaneously
  - 1 line: 60 × (level + 1)
  - 2 lines: 120 × (level + 1)  
  - 3 lines: 360 × (level + 1)
  - 4 lines: 1200 × (level + 1)
  - 5 lines: 4096 × (level + 1)
  - 6 lines: 16384 × (level + 1)
- **Combo Bonus**: Additional points for consecutive line clears
- **Drop Bonus**: 1 point per cell for soft drop, 2 points per cell for hard drop

### Level Progression
- Fall speed increases by ~14.5% each level
- Minimum fall speed prevents game from becoming unplayable

### Special Features
- **Ghost Piece**: Translucent preview showing where piece will land
- **Hold System**: Store one piece for later use (once per piece)
- **Extended Polyominos / Polykings**: Non-standard shapes that connect at vertices

## Compatibility

| Operating System | Status | Notes |
|------------------|--------|-------|
| Linux | ✅ Fully Supported | Tested on Fedora 42 |
| Windows 11 | ✅ Supported | Works with modern Python installations |
| macOS | ❓ Expected to work | Unix-compatible, but untested |

## Troubleshooting

**Error: "Your terminal may not be supported, or it probably is too small"**
- Solution: Increase your terminal window size
- For higher N values, larger terminals may be required

**Colors not displaying correctly:**
- Try different color values (0-255)
- Some terminals may have limited color support
