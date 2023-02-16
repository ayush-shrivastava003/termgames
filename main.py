from pyfiglet import Figlet
from random import randint
import sys
import tty
import termios

FLAG = "\x1b[31m⚑\x1b[0m"
LENGTH = 18
FILENO = sys.stdin.fileno()
OLD_SETTINGS = termios.tcgetattr(FILENO)
FLAGS_LEFT = 40
CORRECT = 0

row = 0
column = 0
board = [[0 for _ in range(LENGTH)] for _ in range(LENGTH)]
covered_board = [["\x1b[42m?\x1b[0m" for _ in range(LENGTH)] for _ in range(LENGTH)]
uncovered = []
flagged = []
bombs = []

def render_board(old):
    termios.tcsetattr(FILENO, termios.TCSADRAIN, OLD_SETTINGS)
    if covered_board[row][column] == "\x1b[42m?\x1b[0m":
        covered_board[row][column] = "?"
    covered_board[row][column] = f"\x1b[41m{covered_board[row][column]}\x1b[0m"
    if not (old[0] == row and old[1] == column):
        fill = "\x1b[42m?\x1b[0m"
        if old in uncovered:
            fill = f"{board[old[0]][old[1]]}"
        elif old in flagged:
            fill = FLAG

        covered_board[old[0]][old[1]] = fill
    sys.stdout.write("\x1bc")

    # print(Figlet(font="small").renderText(f"MINESWEEPER ({floor(time() - START)})"))
    print(Figlet(font="small").renderText(f"MINESWEEPER | {FLAGS_LEFT}"))
    print("-" * (1 + 4*LENGTH))
    for r in covered_board:
        print("| " + " ".join([f"{c} |" for c in r]))
        print("-" * (1 + 4*LENGTH))
    tty.setraw(FILENO)

def generate_board():
    for _ in range(FLAGS_LEFT):
        coords = (randint(0, LENGTH-1), randint(0, LENGTH-1))
        while coords in bombs:
            coords = (randint(0, LENGTH-1), randint(0, LENGTH-1))
        board[coords[0]][coords[1]] = "*"
        bombs.append(coords)

    for r in range(LENGTH):
        for c in range(LENGTH):
            if board[r][c] == "*": continue
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x = r + dx
                    y = c + dy

                    if ((y >= 0 and y < LENGTH) and
                        (x >= 0 and x < LENGTH) and
                        board[x][y] == "*"):
                            board[r][c] += 1

def uncover_area(coords):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            x = coords[0] + dx
            y = coords[1] + dy

            if ((y >= 0 and y < LENGTH) and
                (x >= 0 and x < LENGTH) and
                board[x][y] != "*"):
                covered_board[x][y] = f"{board[x][y]}"
                uncovered.append((x, y))

generate_board()
# middle = floor(LENGTH / 2)
# uncover_area((middle, middle))
render_board((row, column))
# schedule.every().second.do(render_board, (row, column))
while True:
    # schedule.run_pending()
    try:
        if CORRECT == len(bombs):
            raise Exception("You won!")
        
        char = ord(sys.stdin.read(1))
        old = (row, column)

        if char == 27:
            sys.stdin.read(1)
            direction = ord(sys.stdin.read(1))

            if direction == 68: # left
                column = column - 1 if column > 0 else 0
            elif direction == 67: # right
                column = column + 1 if column < LENGTH - 1 else LENGTH - 1
            elif direction == 65: # up
                row = row - 1 if row > 0 else 0
            elif direction == 66: # down
                row = row + 1 if row < LENGTH - 1 else LENGTH - 1

        elif char == 3:
            raise Exception()

        elif char == 102:
            # pass # flag
            coords = (row, column)
            if coords not in flagged and FLAGS_LEFT > 0:
                flagged.append(coords)
                if coords in bombs:
                    CORRECT += 1
                FLAGS_LEFT -= 1
            else:
                flagged.remove(coords)
                if coords in bombs:
                    CORRECT -= 1
                FLAGS_LEFT += 1

        elif char == 32:
            # pass # uncover
            uncovered.append((row, column))
            covered_board[row][column] = board[row][column]
            if board[row][column] == "*":
                # row += 1
                # column += 1
                termios.tcsetattr(FILENO, termios.TCSADRAIN, OLD_SETTINGS)
                for b in bombs:
                    covered_board[b[0]][b[1]] = "\x1b[31m*\x1b[0m"
                
                for f in flagged:
                    if f not in bombs:
                        covered_board[f[0]][f[1]] = "\x1b[44m✗\x1b[0m"

                render_board((row, column))
                raise Exception("You lost!")
            elif board[row][column] == 0:
                uncover_area((row, column))

        render_board(old)
        

    except Exception as e:
        termios.tcsetattr(FILENO, termios.TCSADRAIN, OLD_SETTINGS)
        print(e)
        break


termios.tcsetattr(FILENO, termios.TCSADRAIN, OLD_SETTINGS)