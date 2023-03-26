from numba import jit
import pickle
import random
# import threading


class QLearning:

    # lock = threading.Lock()

    def __init__(self, alpha=0.5, gamma=0.9, epsilon=0.1, Q_values=None):
        """
        Initializes a Q-Learning agent for Othello.

        Args:
            alpha (float): The learning rate, which determines how much the agent weighs new information compared to 
                old information. Default value is 0.5.
            gamma (float): The discount factor, which determines the importance of future rewards. 
                Default value is 0.9.
            epsilon (float): The exploration rate, which determines the probability of taking a random action. 
                Default value is 0.1.
        """
        self._save_path = ".//strategy//QL_dict//my_dict-%s-%s-%s.pickle" % (
            str(alpha), str(gamma), str(epsilon)
        )
        self._ALPHA = alpha
        self._GAMMA = gamma
        self._EPSILON = epsilon

        if Q_values is None:
            try:
                with open(self._save_path, "rb") as f:
                    self._Q_values = pickle.load(f)
            except:
                self._Q_values = {}
        else:
            self._Q_values = Q_values

        self._EXP2 = [
            1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192,
            16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152,
            4194304, 8388608, 16777216, 33554432, 67108864, 134217728,
            268435456, 536870912, 1073741824, 2147483648, 4294967296,
            8589934592, 17179869184, 34359738368, 68719476736, 137438953472,
            274877906944, 549755813888, 1099511627776, 2199023255552,
            4398046511104, 8796093022208, 17592186044416, 35184372088832,
            70368744177664, 140737488355328, 281474976710656, 562949953421312,
            1125899906842624, 2251799813685248, 4503599627370496,
            9007199254740992, 18014398509481984, 36028797018963968,
            72057594037927936, 144115188075855872, 288230376151711744,
            576460752303423488, 1152921504606846976, 2305843009213693952,
            4611686018427387904, 9223372036854775808,
        ]

    def __del__(self):
        self.save_dict()

    def save_dict(self):
        """Write dictionary on files."""
        with open(self._save_path, "wb") as f:
            pickle.dump(self._Q_values, f)

    def update_q_value(self, state, action, reward, next_state):
        """
        Updates the Q-value for a given state-action pair using the Q-Learning algorithm.

        Args:
            state (tuple): The state of the game board represented as a tuple of tuples.
            action (tuple): The action taken by the agent represented as a tuple of coordinates (row, column).
            reward (int): The reward received by the agent for taking the given action.
            next_state (tuple): The resulting state of the game board after taking the given action, represented as a 
                tuple of tuples.
        """
        if self._turn == 0:
            bw_board = [next_state[0], next_state[1]]
        else:
            bw_board = [next_state[1], next_state[0]]

        possible_actions = []
        for num in range(64):
            if (self._EXP2[num]) & self._othello.reversible_area(self._turn, *bw_board):
                possible_actions.append(num)

        if possible_actions != []:
            max_q_next_state = max(
                [self._Q_values.get((next_state, a), 0) for a in possible_actions])
        else:
            max_q_next_state = self._Q_values.get((next_state, action), 0)
        q_value = self._Q_values.get((state, action), 0)
        # Q(s, a) = Q(s, a) + α(r + γmaxQ(s', a') - Q(s, a))
        self._Q_values[(state, action)] = \
            q_value + self._ALPHA * (reward + self._GAMMA*max_q_next_state - q_value)

    def select_action(self, state, possible_actions):
        """
        Selects an action for the agent to take based on the given state and the set of possible actions.

        Args:
            state (tuple): The state of the game board represented as a tuple of tuples.
            possible_actions (list): A list of possible actions that the agent can take, represented as tuples of 
                coordinates (row, column).

        Returns:
            tuple or None: The action selected by the agent, represented as a tuple of coordinates (row, column), or 
                None if there are no possible actions.
        """
        if random.random() < self._EPSILON:
            return random.choice(possible_actions)
        else:
            q_values = {
                a: self._Q_values.get((state, a), 0)
                for a in possible_actions}
            if all(q == 0 for q in q_values):
                return random.choice(self._possible_actions)
            max_q_value = max(q_values.values())
            return random.choice(
                [a for a, q in q_values.items() if q == max_q_value])

    def put_disk(self, othello):
        self._turn = othello.turn
        self._othello = othello

        self._possible_actions = []
        for num in range(64):
            if (self._EXP2[num]) & self._othello.reversible:
                self._possible_actions.append(num)

        # [player, opponent]
        state = self._othello.return_player_board(self._turn)

        # Decide next action
        action = self.select_action(state, self._possible_actions)
        next_state = self._othello.simulate_play(self._turn, action)

        if self._turn == 0:
            next_state = (next_state[0], next_state[1])
        else:
            next_state = (next_state[1], next_state[0])

        # Judge game.
        player, opponent = self._othello.count_disks(*next_state)
        black = self._othello.reversible_area(0, *next_state)
        white = self._othello.reversible_area(1, *next_state)

        reward = 0
        if (black == 0 and white == 0) or (player+opponent) == 64:
            if player > opponent:
                reward = 1
            if player < opponent:
                reward = -1

        self.update_q_value(state, action, reward, next_state)

        return action
