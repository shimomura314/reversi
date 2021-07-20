"""Calculate rating."""

# python -m cProfile -o matching.prof -s tottime matching.py

from concurrent.futures import ProcessPoolExecutor
import cProfile

from bitboard import OthelloGame
from matching import EloRating
from strategy import Strategy


def match(strategies=('random', "min-max")):
    (strategy1, strategy2) = strategies
    count_win = 0
    count_lose = 0
    count_draw = 0

    game = OthelloGame('black')
    game.load_strategy(Strategy)
    game.change_strategy(strategy1, is_player=True)
    game.change_strategy(strategy2, is_player=False)
    game.auto_mode(True)
    while True:
        if game.process_game():
            break

    if game.result == "WIN":
        count_win += 1
    if game.result == "LOSE":
        count_lose += 1
    if game.result == "DRAW":
        count_draw += 1

    game = OthelloGame('white')
    game.load_strategy(Strategy)
    game.change_strategy(strategy1, is_player=True)
    game.change_strategy(strategy2, is_player=False)
    game.auto_mode(True)
    while True:
        if game.process_game():
            break

    if game.result == "WIN":
        count_win += 1
    if game.result == "LOSE":
        count_lose += 1
    if game.result == "DRAW":
        count_draw += 1
    return count_win, count_lose, count_draw


def main(number=2):
    strategies = [
        "random",
        "min-max",
    ]

    Rating = EloRating(strategies)

    parameters = [("random", "min-max") for _ in range(number)]
    results = []

    with ProcessPoolExecutor(max_workers=4) as executor:
        for parameter, result in zip(
                parameters, executor.map(match, parameters)
                ):
            print(parameter, result)
            results.append([parameter, result])
    for parameter, result in results:
        Rating.update_rating(*parameter, 2, result[0]+result[2]/2)
    Rating.save_rating()
    return


if __name__ == "__main__":
    cProfile.run('main()', filename="./matching/matching.prof", sort=2)
