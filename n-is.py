import curses
import random
from math import floor
import argparse as arg
import polyshapes as ps

# constants
BLOCK_CHAR = "█"
BORDER_CHAR = "│"
TOP_BOTTOM_BORDER_CHAR = "─"
CORNER_CHAR = "┌┐└┘"
GAME_NAMES = ["Mono", "D", "Tr", "Tetr", "Pent", "Hex"]

# argument parsing
parser = arg.ArgumentParser(description="Dis/Tris/Tetris/Pentis/Hexis game implementation in Python using curses; use arrow keys to move blocks, 'q' to quit.")
parser.add_argument("n", type=int, nargs='?', help="specifies the number of blocks in the game; use 2 for Distris (2 block), 3 for Tris (3 blocks), 4 for Tetris (4 blocks), and 5 for Pentis (5 blocks), 6 for Hexis (6 blocks)")
parser.add_argument("-e", action="store_true", help="enable 'fun' mode - additional pseudo-polyominos, also called polykings, its quite fun but also hard, only works for Dis, Tris and Tetris game,\
    there are 2 2-polykings, 6 3-polykings, 34 4-polykings and 166 5-polykings, but the game becomes unplayable with 166 pseudo-polyominos, so i only implemented up to 4-polykings")
parser.add_argument("-c", type=str, help="specifies the color of the blocks; use 'r' for red, 'g' for green, 'b' for blue, 'y' for yellow, 'm' for magenta, 'c' for cyan, or 'w' for white.\
    You are able to change those colors with j/k keys for background and u/i keys for main color during game. Number 0-255 are accepted as well")
parser.add_argument("-bc", type=int, help="same as -c, but for background color, only numbers accepted.")
parser.add_argument("-m", action="store_true", help="enable mix mode, includes polyominos/polykings with less than n blocks")

args = parser.parse_args()

# global game state
add_text = ""
level = 0
total_lines = 0
next_shape = None
held_shape = None
can_hold = True
combo_count = 0
last_action_was_clear = False
color, bcgd = curses.COLOR_WHITE, 0

def show_option_menu(stdscr, title, options, option_texts, selected_info=""):
    """Generic function to show a menu with options."""
    selected = 0
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Use arrow keys to navigate, Enter to select")
        
        if selected_info:
            stdscr.addstr(4, 2, selected_info)
            start_y = 6
        else:
            start_y = 3
        
        stdscr.addstr(start_y, 2, title)
        for i, text in enumerate(option_texts):
            prefix = "> " if i == selected else "  "
            stdscr.addstr(start_y + 2 + i, 4, f"{prefix}{text}")
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == 10:  # Enter
            return options[selected]
        elif key >= ord('1') and key <= ord('9'):
            n_value = key - ord('0')
            if n_value <= len(options):
                return options[n_value - 1]

def show_menu(stdscr):
    """Show menu to select n and ext options."""
    curses.curs_set(0)
    
    # fselect n
    n_options = [1, 2, 3, 4, 5, 6]
    n_texts = [f"{n} - {GAME_NAMES[i]}is" for i, n in enumerate(n_options)]
    selected_n = show_option_menu(stdscr, "Select game:", n_options, n_texts)
    if selected_n is None:
        return None, None, None
    
    # select ext
    ext_options = [False, True]
    ext_texts = ["No", "Yes"]
    selected_info = f"Selected: {selected_n} - {GAME_NAMES[selected_n-1]}is"
    selected_ext = show_option_menu(stdscr, "Enable extended polyominos:", ext_options, ext_texts, selected_info)
    if selected_ext is None:
        return None, None, None
    
    # select mix
    mix_options = [False, True]
    mix_texts = ["No", "Yes"]
    selected_mix = show_option_menu(stdscr, "Enable polyominos of lower order:", mix_options, mix_texts, selected_info)
    return selected_n, selected_ext, selected_mix

def initialize_shapes_and_dimensions():
    """Initialize SHAPES, COLS, ROWS, name_of_game, and add_text based on args."""
    global SHAPES, COLS, ROWS, name_of_game, add_text
    
    if not args.m:
        SHAPES = ps.poly[2*args.n - 1] if args.e else ps.poly[2*args.n - 2]
    else:
        SHAPES = []
        for k in range(1, 1+args.n):
            SHAPES = SHAPES + ps.poly[2*k - 1] if args.e else SHAPES + ps.poly[2*k - 2]
    
    name_of_game = GAME_NAMES[args.n - 1] if 1 <= args.n <= 6 else "Mono"
    add_text = "with extended polyominos" if args.e else ""
    
    e = args.n if args.e else 0
    one = 1 if args.n == 1 else 0
    m = -1 if args.m else 0
    COLS = (3 * args.n) + e - 1 + one + m
    ROWS = (5 * args.n) + e

# initialize game settings
if args.n is None:
    # show menu to select n, ext and mix
    try:
        selected_n, selected_ext, selected_mix = curses.wrapper(show_menu)
        if selected_n is None:
            exit(0)
        args.n = selected_n
        args.e = selected_ext
        args.m = selected_mix
    except curses.error as e:
        print("Error running curses menu.")
        print("Your terminal may not be supported.")
        print(f"Curses error: {e}")
        exit(1)


initialize_shapes_and_dimensions()

def rotate_piece(piece):
    return [list(row) for row in zip(*piece[::-1])] # rotates a piece clockwise by transposing and reversing rows... matrices proved to be useful lol

def check_collision(board, piece, offset):
    """
    Check if the piece at the given offset collides with the board
    or goes out of bounds.
    """
    off_x, off_y = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board_x = x + off_x
                board_y = y + off_y
                if not (0 <= board_x < COLS and board_y < ROWS):
                    return True  # out of bounds
                if board_y >= 0 and board[board_y][board_x]:
                    return True  # collision with another piece
    return False

def create_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)] # creates an empty game board

def new_piece():
    """Returns a new random piece dictionary."""
    global next_shape
    shape = next_shape
    next_shape = random.choice(SHAPES)
    for _ in range(random.randint(0, 3)):
        next_shape = rotate_piece(next_shape)
    
    offset = 0
    if args.n < 4:
        offset = random.randint(-1, 1)
    
    return {
        "shape": shape,
        "x": COLS // 2 - len(shape[0]) // 2 + offset,
        "y": 0,
    }

def lock_piece(board, piece):
    """Locks the piece onto the board."""
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                board_y = piece["y"] + y
                board_x = piece["x"] + x
                if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                    board[board_y][board_x] = 1
    return board

def clear_lines(board):
    """Clears completed lines and returns the number of lines cleared."""
    new_board = [row for row in board if not all(row)]
    lines_cleared = ROWS - len(new_board)
    # add new empty lines at the top for each cleared line
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(COLS)])
    return new_board, lines_cleared

def try_wall_kick(board, piece, rotated_shape):
    """Try wall kick positions for rotation."""
    # wall kick offsets to try
    kick_offsets = [
        (0, 0),   # no kick (original position)
        (-1, 0),  # left kick
        (1, 0),   # right kick
        (-2, 0),  # left kick 2
        (2, 0),   # right kick 2
        (-3, 0),  # left kick 2
        (3, 0),   # right kick 2
    ]
    
    for dx, dy in kick_offsets:
        new_x = piece["x"] + dx
        new_y = piece["y"] + dy
        
        # check if the new position is valid
        if not check_collision(board, rotated_shape, (new_x, new_y)):
            return new_x, new_y, rotated_shape
    
    # if no wall kick works, return None
    return None

def calculate_score(lines_cleared, level, combo_count):
    """Calculate score based on Tetris scoring system with level and combo bonuses."""
    if lines_cleared == 0:
        return 0
    
    # base scores for different line clears
    base_scores = {
        1: 60,    # single
        2: 120,   # double  
        3: 360,   # triple
        4: 1200,  # tetris (4 lines)
        5: 4096,  # pentis (5 lines)
        6: 16384, # hexis (6 lines)
    }
    
    # get base score
    base_score = base_scores.get(lines_cleared)
    
    # level multiplier (level + 1 to avoid 0 multiplication)
    level_multiplier = level + 1
    
    # combo bonus
    combo_bonus = combo_count * 50 * level_multiplier * (1+max(0, 4*(args.n - 4))) if combo_count > 0 else 0
    
    # calculate total score
    total_score = (base_score * level_multiplier) + combo_bonus
    
    return total_score

def get_ghost_piece_position(board, piece):
    """Calculate where the piece would land if hard dropped."""
    ghost_y = piece["y"]
    
    # keep moving down until collision
    while not check_collision(board, piece["shape"], (piece["x"], ghost_y + 1)):
        ghost_y += 1
    
    return ghost_y

def draw_progress_bar(stdscr, y, x, width, current, target, label=""):
    """Draw a progress bar showing current/target with visual indicator."""
    if target == 0:
        percentage = 0
    else:
        percentage = min(current / target, 1.0)
    
    filled_width = int(width * percentage)
    
    # draw the bar
    bar = "█" * filled_width + "░" * (width - filled_width)
    stdscr.addstr(y, x, f"{label}[{bar}] {current}/{target}")

def draw_hold_piece(stdscr, start_y, start_x):
    """Draw the held piece in a designated area."""
    global held_shape
    
    stdscr.addstr(start_y, start_x, "HOLD:")
    if held_shape:
        for y, row in enumerate(held_shape):
            for x, cell in enumerate(row):
                if cell:
                    stdscr.addstr(start_y + 1 + y, start_x + x * 2, BLOCK_CHAR * 2)

def draw_game_info(stdscr, score):
    """Draw game information on the right side."""
    global total_lines, combo_count, color, bcgd
    
    stdscr.addstr(0, 0, f"Score: {score}, You are playing {name_of_game}is {add_text}")
    stdscr.addstr(args.n + 2, 3+COLS*2, f"Current level: {level}")
    
    draw_progress_bar(stdscr, args.n + 3, 3+COLS*2, 15, total_lines, 5+level, "Progress: ")
    
    # show combo count if active
    if combo_count > 0:
        stdscr.addstr(args.n + 4, 3+COLS*2, f"Combo: {combo_count}x")
        stdscr.addstr(args.n + 5, 3+COLS*2, f"Current colors are {color} and {bcgd}")
        return args.n + 7
    else:
        stdscr.addstr(args.n + 4, 3+COLS*2, f"Current colors are {color} and {bcgd}")
        return args.n + 6

def draw_border(stdscr):
    """Draw the game border."""
    stdscr.addstr(1, 0, CORNER_CHAR[0] + TOP_BOTTOM_BORDER_CHAR * (COLS * 2) + CORNER_CHAR[1])
    for y in range(ROWS):
        stdscr.addstr(y + 2, 0, BORDER_CHAR)
        stdscr.addstr(y + 2, COLS * 2 + 1, BORDER_CHAR)
    stdscr.addstr(ROWS + 2, 0, CORNER_CHAR[2] + TOP_BOTTOM_BORDER_CHAR * (COLS * 2) + CORNER_CHAR[3])

def draw_game(stdscr, board, piece, score):
    """Draws the entire game state to the screen."""
    stdscr.clear()
    
    # draw game info and get hold position
    hold_y = draw_game_info(stdscr, score)
    
    # draw border
    draw_border(stdscr)

    # draw the board with locked pieces
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addstr(y + 2, x * 2 + 1, BLOCK_CHAR * 2)

    # draw ghost piece (where current piece will land)
    if piece:
        ghost_y = get_ghost_piece_position(board, piece)
        # only draw ghost if it's different from current position
        if ghost_y != piece["y"]:
            for y, row in enumerate(piece["shape"]):
                for x, cell in enumerate(row):
                    if not cell:
                        continue
                    ghost_board_y = ghost_y + y
                    ghost_board_x = piece["x"] + x
                    # check bounds and if position is empty
                    if (0 <= ghost_board_y < ROWS and 0 <= ghost_board_x < COLS and 
                        not board[ghost_board_y][ghost_board_x]):
                        stdscr.addstr(ghost_board_y + 2, ghost_board_x * 2 + 1, "░░")

    # draw the current falling piece
    if piece:
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    if piece["y"] + y >= 0:
                        stdscr.addstr(piece["y"] + y + 2, (piece["x"] + x) * 2 + 1, BLOCK_CHAR * 2)
    
    # draw next piece
    stdscr.addstr(1, 3+COLS*2, "NEXT:")
    for y, row in enumerate(next_shape):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addstr(y + 2, (3 + COLS + x) * 2 + 1, BLOCK_CHAR * 2)
    
    # draw held piece
    draw_hold_piece(stdscr, hold_y, 3+COLS*2)
    
    stdscr.refresh()

def setup_colors():
    """Setup color configuration based on arguments."""
    global color, bcgd
    
    bcgd = args.bc if args.bc is not None else 0
    
    if args.c is not None:
        if args.c.isdigit():
            color = int(args.c)
        else:
            color_map = {
                'r': curses.COLOR_RED,
                'g': curses.COLOR_GREEN,
                'b': curses.COLOR_BLUE,
                'y': curses.COLOR_YELLOW,
                'c': curses.COLOR_CYAN,
                'm': curses.COLOR_MAGENTA
            }
            color = color_map.get(args.c, curses.COLOR_WHITE)

def handle_piece_movement(board, piece, key):
    """Handle piece movement keys."""
    if key == curses.KEY_LEFT:
        if not check_collision(board, piece["shape"], (piece["x"] - 1, piece["y"])):
            piece["x"] -= 1
    elif key == curses.KEY_RIGHT:
        if not check_collision(board, piece["shape"], (piece["x"] + 1, piece["y"])):
            piece["x"] += 1
    elif key == curses.KEY_DOWN:
        if not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
            piece["y"] += 1
            return 1  # soft drop bonus
    elif key == curses.KEY_UP:
        rotated = rotate_piece(piece["shape"])
        wall_kick_result = try_wall_kick(board, piece, rotated)
        if wall_kick_result:
            new_x, new_y, new_shape = wall_kick_result
            piece["x"] = new_x
            piece["y"] = new_y
            piece["shape"] = new_shape
    return 0

def handle_hold_piece(piece):
    """Handle piece holding."""
    global can_hold, held_shape
    if can_hold:
        if held_shape is None:
            held_shape = piece["shape"]
            piece.update(new_piece())
        else:
            temp_shape = piece["shape"]
            piece["shape"] = held_shape
            held_shape = temp_shape
            piece["x"] = COLS // 2 - len(piece["shape"][0]) // 2
            piece["y"] = 0
        can_hold = False

def handle_color_change(stdscr, key):
    """Handle color change keys."""
    global color, bcgd
    
    if key == ord('j') or key == ord('k'):
        bcgd += 1 if key == ord('k') else -1
    if key == ord('u') or key == ord('i'):
        color += 1 if key == ord('u') else -1
    
    bcgd = bcgd % curses.COLORS
    color = color % curses.COLORS
    curses.init_pair(1, color, bcgd)
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)

def handle_hard_drop(board, piece):
    """Handle hard drop and return score bonus."""
    cells_dropped = 0
    while not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
        piece["y"] += 1
        cells_dropped += 1
    return cells_dropped * 2

def show_game_over_screen(stdscr, score):
    """Display game over screen centered in the game board."""
    stdscr.nodelay(0)
    
    # calculate center position within the game board
    board_center_y = ROWS // 2  # board starts at y=2
    board_center_x = 1 + COLS  # board starts at x=1, center is at COLS
    
    try:
        stdscr.addstr(board_center_y - 1, board_center_x - 5, "Game Over!")
        stdscr.addstr(board_center_y, board_center_x - 7, f"Final Score: {score}")
        stdscr.addstr(board_center_y + 3, board_center_x - 8, "Press 'q' to exit")
        stdscr.refresh()
    except curses.error:
        # if drawing fails, clear screen and show simple message
        stdscr.addstr(2*args.n+8, COLS*2+2, f"Game Over! Score: {score}")
        stdscr.addstr(2*args.n+9, COLS*2+2, "Press 'q' to exit")
        stdscr.refresh()
    
    # wait for 'q' key specifically
    while True:
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break

def show_pause_screen(stdscr):
    """Display pause screen centered in the game board."""
    stdscr.nodelay(0)  # disable non-blocking input
    
    # calculate center position within the game board
    board_center_y = ROWS // 2  # board starts at y=2
    board_center_x = 1 + COLS  # board starts at x=1, center is at COLS
    
    try:
        stdscr.addstr(board_center_y, board_center_x - 3, "PAUSED")
        stdscr.addstr(board_center_y + 2, board_center_x - 11, "Press any key to resume")
        stdscr.refresh()
    except curses.error:
        # if drawing fails, clear screen and show simple message
        stdscr.addstr(board_center_y, board_center_x - 3, "PAUSED")
        stdscr.addstr(2*args.n + 8, COLS*2+2, "Press any key to resume")
        stdscr.refresh()
    
    # wait for any key to resume
    stdscr.getch()
    
    # restore non-blocking input
    stdscr.nodelay(1)
    stdscr.timeout(20)

def main(stdscr):
    global next_shape
    next_shape = random.choice(SHAPES)  # initialize the first piece
    """Main game loop."""
    # setup curses
    curses.curs_set(0)
    global level, total_lines, combo_count, last_action_was_clear, can_hold
    
    setup_colors()
    curses.start_color()
    curses.init_pair(1, color, bcgd)  # set color pair for blocks
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    stdscr.nodelay(1)
    stdscr.timeout(20)  # game tick speed like PAL

    # game state initialization
    board = create_board()
    piece = new_piece()
    score = 0
    game_over = False
    fall_counter = 0
    fall_speed = 36  # starting speed, lower is faster
    
    if args.n < 4:
        fall_speed = 36 - 6*(4-args.n)

    while not game_over:
        key = stdscr.getch()
        fall_counter += 1

        # --- handle user input ---
        if key == ord('q') or key == ord('Q'):
            break
        elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP]:
            if key == curses.KEY_DOWN:
                fall_counter = 0  # reset fall counter for soft drop
            score += handle_piece_movement(board, piece, key)
        elif key == ord('c') or key == ord('C'):
            handle_hold_piece(piece)
        elif key in [ord('k'), ord('j'), ord('u'), ord('i')]:
            handle_color_change(stdscr, key)
        elif key == 10:  # hard drop
            fall_counter = fall_speed
            score += handle_hard_drop(board, piece)
        elif key == ord('p'):
            show_pause_screen(stdscr)
        
        # --- game logic (automatic drop) ---
        if fall_counter >= fall_speed:
            fall_counter = 0
            if not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
                piece["y"] += 1
            else:
                # piece has landed, lock it
                board = lock_piece(board, piece)
                board, lines_cleared = clear_lines(board)
                
                # handle scoring with combo system
                if lines_cleared > 0:
                    # if last action was also a line clear, increment combo
                    if last_action_was_clear:
                        combo_count += 1
                    else:
                        combo_count = 0  # reset combo if previous action wasn't a clear
                    
                    # calculate score with level and combo bonuses
                    line_score = calculate_score(lines_cleared, level, combo_count)
                    score += line_score
                    total_lines += lines_cleared
                    last_action_was_clear = True
                else:
                    # no lines cleared, reset combo
                    combo_count = 0
                    last_action_was_clear = False

                # get new piece and allow holding again
                piece = new_piece()
                can_hold = True
                
                # check for game over
                if check_collision(board, piece["shape"], (piece["x"], piece["y"])):
                    game_over = True
        
        if total_lines >= 5+level:
            level += 1
            total_lines = 0
            fall_speed = max(2, floor(fall_speed * 0.855))  # increase speed every 10 lines cleared

        # draw game
        draw_game(stdscr, board, piece, score)

    # game over
    show_game_over_screen(stdscr, score)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as e:
        print("Error running curses.")
        print("Your terminal may not be supported, or it probably is too small.")
        print(f"Curses error: {e}")