"""
BugBit environment for RL training. Abstraction of the Turing Tumble game.
"""

# standard library imports
from copy import deepcopy
from typing import Dict, Any

# 3rd party imports
import pandas as pd
import gym
from gym.utils import seeding

import numpy as np

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities
from dataset_generators.utils import flattened_repr_to_control_flow_matrix, get_outputs


# noinspection PyMethodMayBeStatic
class BugBit(gym.Env):

    def __init__(self, config: dict):
        """
        Initialises the environment.

        :param config: dictionary containing the config for the environment
        :return: None
        """
        super().__init__()
        self.np_random = None
        self.verbose: bool = False

        self.reward: int = 0
        self.done = False
        self.state = None
        self.info: dict = {}
        self.n_bugs: int = 3
        self.config = config
        self.sample_size: int = 4
        self.training_set: pd.DataFrame = pd.DataFrame()
        self.phase: int = 1
        # self.generator: Generator = Generator()
        self.step_counter: int = 0
        self.max_steps: int = 15

        self.parse_config(self.config)

        self.action_space = gym.spaces.Discrete(((2 * self.n_bugs ** 2) // 2 - self.n_bugs))

        # Dictionary containing the state of the environment. Contains the control flow matrix, the input samples,
        # and the output samples.
        self.observation_space = gym.spaces.Dict(
            {
                "control_flow_matrix": gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.n_bugs * (self.n_bugs - 1),), dtype=np.int64
                ),
                "sample_input_pairs": gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.sample_size, self.n_bugs),
                    dtype=np.int64
                ),
                "sample_output_pairs": gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.sample_size, self.n_bugs),
                    dtype=np.int64
                )
            }
        )

    def reset(self) -> Dict[str, Any]:
        """
        Resets the environment and returns the reset state.
        :return:
        """

        self.done = False
        self.reward = 0
        self.info = dict()
        self.step_counter = 0

        row = self._sample_from_training_set()

        self.state = {
            "control_flow_matrix": row["modified_control_flow_matrix"].values[0],
            "sample_input_pairs": row["input_samples"].values[0],
            "sample_output_pairs": row["output_samples"].values[0]
        }

        return self.state

    def step(self, action: int):
        """
        Step function of the environment
        :param action: edge in the control flow matrix to be set/unset
        :return:
        """
        # 1. Check if the maximum number of steps has reached and, if so, end the game
        self.step_counter += 1
        if self.step_counter > self.max_steps:
            self.reward = -1
            self.done = True
            self.info = {
                "won": 0
            }
            return [self.state, self.reward, self.done, self.info]

        # 2. Take the action the agent selected (i.e. set/unset an edge)
        cf_matrix = deepcopy(self.state["control_flow_matrix"])

        cf_matrix[action] = 1 if cf_matrix[action] == 0 else 0

        # 3. Get the outputs for the corresponding input pairs for the (now) modified control flow matrix
        current_outs = get_outputs(
            n_bugs=self.n_bugs,
            ins=self.state["sample_input_pairs"],
            prog=flattened_repr_to_control_flow_matrix(flat_cf_repr=cf_matrix, n_bugs=self.n_bugs)
        )
        # 4. Update the state
        self.state = {
            "control_flow_matrix": cf_matrix,
            "sample_input_pairs": self.state["sample_input_pairs"],
            "sample_output_pairs": self.state["sample_output_pairs"]
        }

        # 5. If the outputs in the observations space equal the ones of the updated control flow matrix
        # return a positive reward and end the game
        if np.array_equal(current_outs, self.state["sample_output_pairs"]):
            self.reward = 1
            self.done = True
            self.info = {
                "won": 1
            }
        # 6. else keep the reward at 0 and let the game continue
        else:
            self.reward = -1
            self.done = False
        return [self.state, self.reward, self.done, self.info]

    def render(self, mode: str = "human"):
        """
        Render method of the environment. Not implemented for bugbit.
        :param mode:
        :return: None
        """
        raise NotImplementedError("render() is not implemented")

    def parse_config(self, config: dict):
        """
        Parses the config dictionary that is passed in __init__
        :param config: dictionary containing the config for the environment
        :return: None
        """
        self.config = config
        self.n_bugs = config.get("n_bugs")
        self.training_set = config.get("training_set")
        self.max_steps = config.get("max_steps")
        self.sample_size = config.get("sample_size")

    def _sample_from_training_set(self) -> pd.Series:
        """
        Takes a random sample from the training set depending on the phase the environment is set to
        :return:
        """
        return self.training_set.loc[self.training_set["distance"] == self.phase].sample(n=1)

    def increment_phase(self):
        """
        Set the phase (i.e. difficulty for curriculum learning) of the environment.
        Also increases the maximum number of steps for the next phase.
        Follows: https://docs.ray.io/en/releases-1.3.0/rllib-training.html#curriculum-learning
        :return: None
        """
        if self.phase < self.training_set["distance"].max():
            self.phase += 1
            self.max_steps += 1
            print("Phase incremented to: ", self.phase)
        else:
            print("Maximum phase reached!")

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.
        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def close(self):
        """
        Close method of the environment. Not implemented for bugbit.
        :return: None
        """
        pass
