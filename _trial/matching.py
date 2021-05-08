"""Calculate rating."""

from itertools import combinations
import pickle
import time
import timeit
from tqdm import tqdm

from bitboard import OthelloGame
from matching import EloRating
from strategy import Strategy


def matching(strategy1, strategy2, matching_number):
    """Returns the number of strategy1's result.

    Parameters
    ----------
    strategy1, strategy2 : str
        Names of used strategies.

    matching_number : int
        Number of matches.

    Returns
    ----------
    count_win, count_lose, count_draw : int
        result of matches.
    """
    if strategy1 == strategy2:
        return
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
        if strategy1 == "min-max simple":
            game._Strategy_player._strategy.update_file()
        if strategy2 == "min-max simple":
            game._Strategy_opponent._strategy.update_file()
        if strategy1 == "min-max":
            game._Strategy_player._strategy.update_file()
        if strategy2 == "min-max":
            game._Strategy_opponent._strategy.update_file()

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

        if strategy1 == "min-max simple":
            game._Strategy_player._strategy.update_file()
        if strategy2 == "min-max simple":
            game._Strategy_opponent._strategy.update_file()
        if strategy1 == "min-max":
            game._Strategy_player._strategy.update_file()
        if strategy2 == "min-max":
            game._Strategy_opponent._strategy.update_file()

        if game.result == "WIN":
            count_win += 1
        if game.result == "LOSE":
            count_lose += 1
        if game.result == "DRAW":
            count_draw += 1
    print(strategy1, "vs", strategy2, count_win, "勝", count_lose, "敗", count_draw, "分")
    return count_win, count_lose, count_draw


def initialize_rate(strategies):
    Rating = EloRating(strategies)
    Rating.initialize_rating()
    Rating.save_rating()


def rerating(strategies, number):
    Rating = EloRating(strategies)
    for strategy1, strategy2 in combinations(strategies, 2):
        count_win, count_lose, count_draw = matching(strategy1, strategy2, matching_number=number)
        Rating.update_rating(strategy1, strategy2, number*2, count_win+count_draw/2)
    Rating.save_rating()
    print(Rating._rating)


def main(strategies, game_number=1, repeat=20):
    progress_bar = tqdm(total=repeat)
    progress_bar.set_description('Number of matches.')
    for _ in range(repeat):
        rerating(strategies, game_number)
        progress_bar.update(1)
    progress_bar.close()
    print('Game was played', int((game_number*2)*repeat*len(strategies)*(len(strategies)-1)//2), "times.")
    return


if __name__ == "__main__":
    strategies = [
    "random",
    # "maximize",
    # "minimize",
    # "min-max simple",
    "min-max",
    ]

    main(strategies, repeat=10)
    # initialize_rate(strategies)