"""Various strategies for othello.
"""

from bitboard import OthelloGame

from .maximize import Maximize
from .minimize import Minimize
from .minmax import Minmax
from .minmaxsimple import MinmaxSimple
from .random import Random


class Strategy(OthelloGame):
    """You can select AI strategy from candidates below.

    Strategies
    ----------
    random : Put disk randomly.
    maximize : Put disk to maximize number of one's disks.
    minimize : Put disk to minimize number of one's disks.
    openness : Put disk based on openness theory.
    evenness : Put disk based on evenness theory.
    """
    def __init__(self, othello):
        self._othello = othello
        self._player_color = othello._player_color
        self._strategy = Random()
        return

    def set_strategy(self, strategy: str):
        if strategy == "random":
            self._strategy = Random()
        if strategy == "maximize":
            self._strategy = Maximize()
        if strategy == "minimize":
            self._strategy = Minimize()
        if strategy == "min-max simple":
            self._strategy = MinmaxSimple()
        if strategy == "min-max":
            self._strategy = Minmax()
        return

    def selecter(self, othello):
        return self._strategy.put_disk(othello)
