"""Various strategies for othello.
"""

import random


class Maximize:
    """Put disk to maximize number of one's disks."""
    def __init__(self):
        return

    def put_disk(self, othello):
        """Put disk to maximize number of one's disks."""
        game_turn = othello.game_turn
        white_board, black_board = othello.board.return_board()
        max_strategy = []
        max_merit = 0

        candidates = []
        for num in range(64):
            if (pow(2, num)) & othello.reversible:
                candidates.append(num)
        for candidate in candidates:
            new_board = othello.board.play_turn(
                othello.game_turn, candidate, update=False
                )
            counter = othello.board.count_disks(*new_board)
            counter[game_turn]
            if max_merit < counter[game_turn]:
                max_strategy = [candidate]
                max_merit = counter[game_turn]
            elif max_merit == counter[game_turn]:
                max_strategy.append(candidate)
        return random.choice(max_strategy)
