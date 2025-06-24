# N-is: A Generalized Tetris Game

N-is is a terminal-based puzzle game that generalizes the classic Tetris concept to work with polyominos of any size from 2 to 5 blocks. Play traditional Tetris (4 blocks) or experiment with Tris (3 blocks), Dis (2 blocks), or even challenging Pentis (5 blocks)!

<figure>
    <img src="./example.png"
         alt="...">
    <figcaption>Example game of tetris with extended mode enabled.</figcaption>
</figure>


## What It Does

- **Flexible Block Size**: Choose your game style with different block counts:
  - 1: "Mono" (single blocks)
  - 2: "Dis" (domino shapes)
  - 3: "Tris" (triomino shapes)
  - 4: "Tetris" (classic tetromino shapes)
  - 5: "Pentis" (pentomino shapes - more challenging!)

- **Fun Mode**: Enable extended mode with `-e` flag to add non-standard polyominos (that can connect at vertices)

- **Customizable**: Choose your preferred block color with -c flag

- **Traditional Gameplay**: Features standard mechanics like:
  - Line clearing
  - Piece rotation
  - Scoring based on lines cleared
  - Increasing difficulty

## How to Run

```bash
python n-is.py <N> [-e] [-c COLOR]
```

or:

```bash
py n-is.py <N> [-e] [-c COLOR]
```

or:

```bash
./executable/n-is <N> [-e] [-c COLOR]
```

It also can be compiled with:

```bash
pyinstaller n-is.py
```
the executable can be found in dist directory.


You can display help with:
```bash
python n-is.py -h
```

### Arguments:

- `N`: Required - specifies the number of blocks (2-5)
- `-e`: Optional - enables "fun" mode with additional shape variations
- `-c`: Optional - specifies the block color:
  - `r`: red
  - `g`: green
  - `b`: blue
  - `y`: yellow
  - `m`: magenta
  - `c`: cyan
  - `w`: white (default)
- `-h`: Shows help message
### Examples:

```bash
python n-is.py 4        # Classic Tetris
python n-is.py 3 -e     # Tris with extended polyminos
python n-is.py 5 -c g   # Pentis with green blocks
```

### Controls:

- **Left/Right Arrow**: move piece horizontally
- **Down Arrow**: drop
- **Up Arrow**: rotate piece
- **q**: quit game
- **u/i**: change main color
- **j/k**: change background color


## Dependencies

- Python 3.x
- curses, random and argparse libraries (included in standard Python installation)

The game is designed for terminal environments with adequate size. If you encounter this error:
```
Error running curses.
Your terminal may not be supported, or it probably is too small.
Curses error: addwstr() returned ERR
```
try increasing your terminal window size.

## Compatibility

| Operating System | Supported  | Notes                                          |
|------------------|------------|------------------------------------------------|
| Linux            | ✓          | Fully supported, tested on Fedora 42           |
| Windows 11       | ✓          | It works with new python installed             |
| macOS            | ?          | Expected to work properly (Unix-compatible), but i dont own a macOS machine to test this          |

## Why I Created This

I created N-is as an exploration of the Tetris concept, extending it to work with different polyomino sizes. This project demonstrates how the core mechanics of Tetris can be generalized, creating both simpler versions (Dis/Tris) and more complex versions (Pentis).

The "fun" mode with non-standard shapes adds another layer of challenge and demonstrates how breaking traditional polyomino rules can lead to harder gameplay

It also serves as a practical example of terminal-based game development using Python and the curses library, showing how to handle user input, game logic, and rendering in a text-based environment.
