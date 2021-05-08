"""Calculate rating."""

import pickle


class EloRating:
    """Load and update Rating."""
    INIT_RATING = 1500
    K = 16

    def __init__(self, members, filename='./_trial/matching/strategy_rating.pkl'):
        self._filename = filename
        try:
            with open(filename, 'rb') as file_:
                self._rating = pickle.load(file_)
        except:
            self._rating = {}
        for member in members:
            if not member in self._rating:
                self._rating[member] = EloRating.INIT_RATING
        return

    def save_rating(self):
        with open(self._filename, 'wb') as file_:
            pickle.dump(self._rating, file_)

    def win_lose_ratio(self, member1: str, member2: str):
        """Calculate ratio in which member1 wins."""
        rate_difference = self._rating[member2]-self._rating[member1]
        ratio = 1/(pow(10, rate_difference/400)+1)
        return ratio

    def update_rating(self, member1: str, member2: str, number_game: int, number_1_win: int):
        """Update rating.

        Parameters
        ----------
        member1, member2 : str
            Names of used members.

        number_game : int
            Number of matches.

        number_1_win : int
            NUmber of the matches member1 won.
        """
        number_2_win = number_game - number_1_win
        pre_probability_1 = self.win_lose_ratio(member1, member2)
        expected_win_1 = pre_probability_1 * number_game
        pre_probability_2 = self.win_lose_ratio(member2, member1)
        expected_win_2 = pre_probability_2 * number_game

        self._rating[member1] = self._rating[member1] + EloRating.K*(number_1_win-expected_win_1)
        self._rating[member2] = self._rating[member2] + EloRating.K*(number_2_win-expected_win_2)
        return

    def initialize_rating(self):
        for member in self._rating.keys():
            self._rating[member] = EloRating.INIT_RATING
        return