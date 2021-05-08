"""Various strategies for othello.
"""

import random


class Minimize:
    """Put disk to minimize number of one's disks."""
    def __init__(self):
        return

    def put_disk(self, othello):
        """Put disk to minimize number of one's disks."""
        black_board = othello.board._black_board
        white_board = othello.board._white_board
        game_turn = othello.board.game_turn
        min_strategy = []
        min_merit = float('inf')

        candidates = []
        for num in range(64):
            if (pow(2, num))&othello.reversible:
                candidates.append(num)

        for candidate in candidates:
            new_black_board, new_white_board = othello.board.reverse(black_board, white_board, game_turn, pow(2, candidate))
            count_player, count_opponent = othello.board.count_disks(new_black_board, new_white_board, game_turn)
            if min_merit > count_player:
                min_strategy = [candidate]
                min_merit = count_player
            elif min_merit == count_player:
                min_strategy.append(candidate)
        return random.choice(min_strategy)