"""Calculate rating."""

# python -m cProfile -o matching.prof -s tottime matching.py

import cProfile
from itertools import combinations
import pickle
import time
import timeit
from tqdm import tqdm

from bitboard import OthelloGame
from matching import EloRating
from strategy import Strategy


def matching(strategy1, strategy2, matching_number):
    count_win = 0
    count_lose = 0
    count_draw = 0

    for _ in range(matching_number):
        game = OthelloGame('black')
        game.load_strategy(Strategy)
        game.change_strategy(strategy1, is_player=True)
        game.change_strategy(strategy2, is_player=False)
        game.auto_mode(True)
        while True:
            if game.process_game():
                break

        # if strategy1 == "min-max":
        #     game._Strategy_player._strategy.update_file()
        # if strategy2 == "min-max":
        #     game._Strategy_opponent._strategy.update_file()

        if game.result == "WIN":
            count_win += 1
        if game.result == "LOSE":
            count_lose += 1
        if game.result == "DRAW":
            count_draw += 1

    for _ in range(matching_number):
        game = OthelloGame('white')
        game.load_strategy(Strategy)
        game.change_strategy(strategy1, is_player=True)
        game.change_strategy(strategy2, is_player=False)
        game.auto_mode(True)
        while True:
            if game.process_game():
                break

        # if strategy1 == "min-max":
        #     game._Strategy_player._strategy.update_file()
        # if strategy2 == "min-max":
        #     game._Strategy_opponnt._strategy.update_file()

        if game.result == "WIN":
            count_win += 1
        if game.result == "LOSE":
            count_lose += 1
        if game.result == "DRAW":
            count_draw += 1
    return count_win, count_lose, count_draw


def main(game_number=1):
    strategies = [
    "random",
    "min-max",
    ]

    Rating = EloRating(strategies)
    count_win, count_lose, count_draw = matching("random", "min-max", matching_number=game_number)
    Rating.update_rating("random", "min-max", game_number*2, count_win+count_draw/2)
    Rating.save_rating()
    return


if __name__ == "__main__":
    cProfile.run('main()', filename="./matching/matching.prof", sort=2)