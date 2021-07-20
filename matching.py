"""Calculate rating."""

from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from tqdm import tqdm

from bitboard import OthelloGame
from matching import EloRating
from strategy import Strategy


def initialize_rate(strategies):
    Rating = EloRating(strategies)
    Rating.initialize_rating()
    Rating.save_rating()


def set_match(strategy1, strategy2, color):
    game = OthelloGame(color)
    game.load_strategy(Strategy)
    game.change_strategy(strategy1, is_player=True)
    game.change_strategy(strategy2, is_player=False)
    game.auto_mode(True)
    while True:
        if game.process_game():
            break
    return game.result


def matching(strategies):
    """Returns the number of strategy1's result.

    Parameters
    ----------
    strategies : list of str
        Names of used strategies.

    matching_number : int
        Number of matches.

    Returns
    ----------
    count_win, count_lose, count_draw : int
        result of matches.
    """
    (strategy1, strategy2) = strategies
    if strategy1 == strategy2:
        return

    count_win = 0
    count_lose = 0
    count_draw = 0

    result = set_match(strategy1, strategy2, "black")
    if result == "WIN":
        count_win += 1
    if result == "LOSE":
        count_lose += 1
    if result == "DRAW":
        count_draw += 1

    result = set_match(strategy1, strategy2, "white")
    if result == "WIN":
        count_win += 1
    if result == "LOSE":
        count_lose += 1
    if result == "DRAW":
        count_draw += 1

    print("%s vs %s : %d wins, %d loses, and %d draws" % (
        strategy1, strategy2, count_win, count_lose, count_draw))
    return count_win, count_lose, count_draw


def main(repeat=10):
    strategies = [
        "random",
        "maximize",
        "minimize",
        "min-max simple",
        "min-max",
    ]

    parameters = []
    for _ in range(repeat):
        for strategy1, strategy2 in combinations(strategies, 2):
            parameters.append((strategy1, strategy2))

    progress_bar = tqdm(total=len(parameters))
    progress_bar.set_description('Number of matches.')

    Rating = EloRating(strategies)
    results = []

    with ProcessPoolExecutor(max_workers=4) as executor:
        for parameter, result in zip(
                parameters, executor.map(matching, parameters)
                ):
            results.append([parameter, result])
            progress_bar.update(1)
    for parameter, result in results:
        Rating.update_rating(*parameter, 2, result[0]+result[2]/2)
    Rating.save_rating()
    print(Rating._rating)
    progress_bar.close()
    print('Game was played', len(parameters)*2, "times.")
    return


if __name__ == "__main__":
    main(10)
