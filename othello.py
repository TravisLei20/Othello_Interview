#!/usr/bin/env python3
"""
Othello, also known as Reversi, is a game between two players, denoted by black
and white.

Play happens on an 8x8 grid. Game pieces are discs with a black side and a
white side. The face-up side of a piece indicates its current owner.

The game begins with two black pieces and two white pieces, as shown:

  a b c d e f g h 
1                
2                
3                
4      B W       
5      W B       
6                
7                
8                

Players alternate turns, beginning with black.

A player's turn consists of placing a new piece of their color on an empty space
and then flipping the opponent's pieces.

A player flips lines of one or more opposing pieces when they are bookended
(surrounded) by the newly placed piece and one of their existing pieces. The line
including the bookends must be contiguous (no gaps). Lines of flipped pieces
can be othogonal or diagonal. Multiple lines may be flipped in a single turn.
(Note: One of the two surrounding pieces MUST be the newly placed piece.)

For example, in the following game, black plays g6. This move flips the white
pieces at c6, d6, e6, f5, and f6 to black.

  a b c d e f g h       a b c d e f g h       a b c d e f g h
1                     1                     1                
2                     2                     2                
3       W B W         3       W B W         3       W B W    
4     W B B W B       4     W B B W B       4     W B B W B  
5   W B W B W         5   W B W B *         5   W B W B B    
6   B W W W W         6   B * * * * B       6   B B B B B B  
7                     7                     7                
8                     8                     8                

Every move must flip at least one piece. If a player cannot move, their turn is
skipped.

For example, in the following game, white has no legal move:

  a b c d e f g h
1       W W W   W
2     W W W W   W
3   W W W B W W W
4     W B B W B W
5 W W W W W W B W
6   W W W W W W W
7     W W W W W W
8 B B B B B B B W

When neither player can move, the game ends.

At the end of the game, the player with the most pieces wins. If players have
the same number of pieces, the game is a tie.

Write a program that two people can use to play a game of Othello.

A fully working program should:
  * validate attempted moves
  * execute moves
  * skip turns
  * end the game
  * display the winner

If you have extra time, create a simple AI to play the game.

Pace your development such that the program works as much as possible by the
end of the alloted time; i.e. it should not be in a "broken" state.

"""

import enum
import io
import re
import sys
import typing


class Color(enum.Enum):
    BLACK = "B"
    WHITE = "W"


class Coordinate:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return (
            isinstance(other, Coordinate)
            and self.row == other.row
            and self.col == other.col
        )

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return "Coordinate(row={}, col={})".format(self.row, self.col)


Coordinate = typing.Tuple[int, int]
Board = typing.List[typing.List[Color]]

SIZE = 8


class CoordinateParseError(Exception):
    pass


def parse_coordinate(str) -> Coordinate:
    if len(str) != 2:
        raise CoordinateParseError("Input must be length 2")
    str = str.lower()
    row = ord(str[1]) - ord("1")
    if not (0 <= row < SIZE):
        raise CoordinateParseError("Row out of bounds")
    col = ord(str[0]) - ord("a")
    if not (0 <= col < SIZE):
        raise CoordinateParseError("Col out of bounds")
    return (row, col)


def board_str(board: Board) -> str:
    result = f"  {' '.join(chr(ord('a') + i) for i in range(SIZE))}\n"
    for i, row in enumerate(board):
        result += f"{i + 1} {' '.join(position.value if position else ' ' for position in row)}\n"
    return result


def is_board_full(board: Board) -> bool:
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True

def count_tokens_and_determine_winner(board):
    black_count = 0
    white_count = 0

    for row in board:
        for cell in row:
            if cell == Color.BLACK:
                black_count += 1
            elif cell == Color.WHITE:
                white_count += 1

    if black_count > white_count:
        return "Black wins!"
    elif white_count > black_count:
        return "White wins!"
    else:
        return "It's a tie!"


def no_valid_moves(board: Board, color: Color) -> bool:
    for row in range(SIZE):
        for col in range(SIZE):
            if valid_move(board, color, (row, col)):
                return False
    return True


def find_adjacent(board: Board, move: Coordinate, color: Color) -> bool:
    # check adjacent spots
    adjacents = [
        (move[0] + 1, move[1]),
        (move[0] - 1, move[1]),
        (move[0], move[1] + 1),
        (move[0], move[1] - 1),
        (move[0] + 1, move[1] + 1),
        (move[0] + 1, move[1] - 1),
        (move[0] - 1, move[1] + 1),
        (move[0] - 1, move[1] - 1)
    ]
    opposite_color = Color.BLACK if color == Color.WHITE else Color.WHITE
    for adj_row, adj_col in adjacents:
        try:
            if board[adj_row][adj_col] == opposite_color:
                return True
        except IndexError:
            continue  # Skip to the next adjacent spot if an IndexError occurs
    
    return False


def is_flippable_line(board, move, color, direction, found_opponent=False):
    row, col = move
    d_row, d_col = direction
    row += d_row
    col += d_col

    # Base cases
    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return False
    if board[row][col] is None:
        return False
    if board[row][col] == color:
        return found_opponent

    # Recursive case
    return is_flippable_line(board, (row, col), color, direction, True)


def valid_move(board: Board, color: Color, move: Coordinate) -> bool:
    # check if move is within bounds
    if not (0 <= move[0] < SIZE and 0 <= move[1] < SIZE):
        return False
    # check if board pos is empty
    if board[move[0]][move[1]] is not None:
        return False
    # check if move has adjacent opp color
    if not find_adjacent(board, move, color):
        return False
    # check if move can flip opponents
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for direction in directions:
        if is_flippable_line(board, move, color, direction):
            return True
    return False
    

def do_flip(board: Board, color: Color, move: Coordinate):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def flip_line(board, move, color, direction):
        row, col = move
        d_row, d_col = direction
        row += d_row
        col += d_col
        while board[row][col] != color:
            board[row][col] = color
            row += d_row
            col += d_col

    for direction in directions:
        if is_flippable_line(board, move, color, direction):
            flip_line(board, move, color, direction)


def play_game(input):
    board = [[None] * SIZE for _ in range(SIZE)]
    board[3][3] = Color.BLACK
    board[3][4] = Color.WHITE
    board[4][3] = Color.WHITE
    board[4][4] = Color.BLACK

    turn = Color.BLACK

    skip = 0

    while True:
        print(board_str(board))

        try:
            if no_valid_moves(board, turn):
                print(f"{turn.name.lower()} has no valid moves. Skipping turn.")
                turn = Color.WHITE if turn == Color.BLACK else Color.BLACK
                print()
                skip += 1
                if skip >= 2:
                    print(count_tokens_and_determine_winner(board))
                    break
                continue
            skip = 0 
            print(f"Enter move for {turn.name.lower()}: ")
            str = next(input)
            move = parse_coordinate(str.rstrip())
        except CoordinateParseError as e:
            print(f"Invalid move: {e}")
            print()
            continue
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            break

        valid_board = board.copy()

        if not valid_move(valid_board, turn, move):
            print("Invalid move. Try again.")
            continue

        board[move[0]][move[1]] = turn
        do_flip(board, turn, move)

        # Switch Turns
        turn = Color.WHITE if turn == Color.BLACK else Color.BLACK

        print()


def main():
    input = sys.stdin
    play_game(input)


main()