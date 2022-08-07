"""
The Connect Four environment Python adaptation of the original Java Implementation (connectfour.ConnectFour.java)
"""
# standard library imports

from typing import List

# 3rd party imports
import gym
# noinspection PyPackageRequirements
import jpype
import numpy as np

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities


# noinspection PyAbstractClass
class ConnectFourMVC(gym.Env):
    done: bool = False
    reward: int = None
    state: List[List[int]] = None
    connectfour: jpype.JClass = None
    config: str
    info: dict = {}
    view = None
    winner: int = 0

    metadata = {
        "render.modes": ["human"]
    }

    def __init__(self):
        """
        Initialises the environment.

        :return: None
        """
        self.winner: int = 0
        self.action_space: gym.spaces.Space = gym.spaces.Discrete(7)
        self.observation_space: gym.spaces.Space = gym.spaces.Box(0, 2, shape=(6, 7))
        self.connectfour: jpype.JClass = jpype.JClass("connectfour.ConnectFour")()
        # noinspection PyTypeChecker
        self.state: np.ndarray = np.array(self.connectfour.reset())

    def reset(self):
        """
        Resets the environment (e.g. after a game has ended)

        :return:
        """
        self.reward = 0
        self.done = False
        return np.array(self.connectfour.reset())

    def step(self, action: int) -> list:
        """
        Step function of the environment.

        :param action: Integer representing the action to take
        :return: state, reward, done, info
        """
        self.state, self.reward, self.done, self.info, winner = self.connectfour.step(action)
        # noinspection PyTypeChecker
        self.state = np.array(self.state)
        self.reward = int(self.reward)
        self.done = bool(self.done)
        self.info = {}

        return [self.state, self.reward, self.done, self.info]

    def return_reward(self) -> int:
        """
        Returns the reward obtained in the current step

        :return: An Integer describing the reward.
        """
        return self.reward

    def return_done(self) -> bool:
        """
        Returns whether the game is over or not.

        :return: A Boolean. True = Done, False = Not Done
        """
        return self.done

    def return_winner(self) -> int:
        """
        Returns the winner of a finished game

        :return: An integer indicating who won the game.
        """
        return self.winner

    def get_greedy_action(self, agent_id: int) -> int:
        """
        Returns the next action of the greedy player.

        :param agent_id: specifies which ´id´ the greedy agent is (1 or 2)
        :return: int indicating the next action of the greedy player.
        """
        return int(self.connectfour.getGreedyAction(agent_id))

    def interactive_step(self, action: int, agent_id: int) -> list:
        """
        Interactive step such that only one action is taken at a time (either RL agent or heuristic/greedy agent)

        :param action: which column to place a token in
        :param agent_id: which agent is placing the token (either [heuristic/greedy]/human or RL agent; i.e. 1 or 2
        (some integer))
        :return: returns the new state after taking the step
        """
        self.state, self.reward, self.done, self.info, winner = self.connectfour.step(action, agent_id)
        # noinspection PyTypeChecker
        self.state = np.array(self.state)
        self.reward = int(self.reward)
        self.done = bool(self.done)
        self.info = {}

        return [self.state, self.reward, self.done, self.info]
