"""Various strategies for othello.
"""

import random


class Maximize:
    """Put disk to maximize number of one's disks."""
    def __init__(self):
        return

    def put_disk(self, othello):
        """Put disk to maximize number of one's disks."""
        black_board = othello.board._black_board
        white_board = othello.board._white_board
        game_turn = othello.board.game_turn
        max_strategy = []
        max_merit = 0

        candidates = []
        for num in range(64):
            if (pow(2, num))&othello.reversible:
                candidates.append(num)

        for candidate in candidates:
            new_black_board, new_white_board = othello.board.reverse(black_board, white_board, game_turn, pow(2, candidate))
            count_player, count_opponent = othello.board.count_disks(new_black_board, new_white_board, game_turn)
            if max_merit < count_player:
                max_strategy = [candidate]
                max_merit = count_player
            elif max_merit == count_player:
                max_strategy.append(candidate)
        return random.choice(max_strategy)