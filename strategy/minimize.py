"""Various strategies for othello.
"""

import random


class Minimize:
    """Put disk to minimize number of one's disks."""
    def __init__(self):
        return

    def put_disk(self, othello):
        """Put disk to minimize number of one's disks."""
        game_turn = othello.game_turn
        white_board, black_board = othello.board.return_board()
        min_strategy = []
        min_merit = float("inf")

        candidates = []
        for num in range(64):
            if (pow(2, num)) & othello.reversible:
                candidates.append(num)
        for candidate in candidates:
            new_board = othello.board.put_disk(
                othello.game_turn, candidate, update=False
                )
            counter = othello.board.count_disks(*new_board)
            counter[game_turn]
            if min_merit > counter[game_turn]:
                min_strategy = [candidate]
                min_merit = counter[game_turn]
            elif min_merit == counter[game_turn]:
                min_strategy.append(candidate)
        return random.choice(min_strategy)
