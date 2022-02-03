"""A strategy to try to maximize the number of disks you have."""

import random


class Maximize:
    def __init__(self):
        return

    def put_disk(self, othello):
        game_turn = othello.game_turn
        max_strategy = []
        max_merit = 0

        candidates = []
        for num in range(64):
            if (pow(2, num)) & othello.reversible:
                candidates.append(num)
        for candidate in candidates:
            new_board = othello.board.simulate_play(
                othello.game_turn, candidate)
            counter = othello.board.count_disks(*new_board)
            print(counter, new_board, "b")
            if max_merit < counter[game_turn]:
                max_strategy = [candidate]
                max_merit = counter[game_turn]
            elif max_merit == counter[game_turn]:
                max_strategy.append(candidate)
        print(max_strategy)
        return random.choice(max_strategy)
