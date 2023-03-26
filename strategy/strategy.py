"""Various strategies for othello."""

from bitboard import OthelloGame

from .maximize import Maximize
from .minimize import Minimize
from .minmaxcalc import MinmaxC
from .qlearning import QLearning
from .random import Random


class Strategy(OthelloGame):
    """You can select AI strategy from candidates below.

    Strategies
    ----------
    random : Put disk randomly.
    maximize : Put disk to maximize number of one's disks.
    minimize : Put disk to minimize number of one's disks.
    min-max : Put disk based on min-max theory.
    """

    def __init__(self, othello, strategy: str = "random"):
        self._othello = othello
        self._player_clr = othello.return_turn()
        self.set_strategy(strategy)

    def set_strategy(self, strategy: str):
        if strategy == "random":
            self._strategy = Random()
        elif strategy == "maximize":
            self._strategy = Maximize()
        elif strategy == "minimize":
            self._strategy = Minimize()
        elif strategy == "min-max short":
            self._strategy = MinmaxC(2)
        elif strategy == "min-max":
            self._strategy = MinmaxC(4)
        elif strategy == "min-max long":
            self._strategy = MinmaxC(6)
        elif strategy == "QLearning":
            self._strategy = QLearning()
        else:
            raise KeyError

    def selecter(self, othello):
        return self._strategy.put_disk(othello)
