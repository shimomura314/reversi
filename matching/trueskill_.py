"""Calculate rating."""

import pickle

import trueskill


class TrueSkill:
    """Load and update Rating."""

    def __init__(self, members, filename="./matching/trueskill.pkl"):
        self._filename = filename
        try:
            with open(filename, "rb") as file_:
                self._rating = pickle.load(file_)
        except FileNotFoundError:
            self._rating = {}
        for member in members:
            if member not in self._rating:
                self._rating[member] = trueskill.Rating()

    def save_rating(self):
        with open(self._filename, "wb") as file_:
            pickle.dump(self._rating, file_)

    def update_rating(
            self, rating1: trueskill.Rating, rating2: trueskill.Rating,
            drawn: bool = False):
        """Update rating.

        Parameters
        ----------
        member1 : trueskill.Rating
            The winner’s rating if they didn’t draw.
        member2 : trueskill.Rating
            The loser’s rating if they didn’t draw.
        drawn : bool
            If the players drew, set this to True. Defaults to False.
        """
        self._rating[rating1], self._rating[rating2] = trueskill.rate_1vs1(
            self._rating[rating1], self._rating[rating2], drawn = drawn
        )

    def initialize_rating(self):
        for member in self._rating.keys():
            self._rating[member] = trueskill.Rating()

    def printer(self):
        for key in self._rating:
            print(key, self._rating[key].mu, self._rating[key].sigma)

    def returner(self):
        keys = []
        mus = []
        sigmas = []
        for key in self._rating:
            keys.append(key)
            mus.append(self._rating[key].mu)
            sigmas.append(self._rating[key].sigma)
            # rslt.append([key, self._rating[key].mu, self._rating[key].sigma])
        return keys, mus, sigmas
