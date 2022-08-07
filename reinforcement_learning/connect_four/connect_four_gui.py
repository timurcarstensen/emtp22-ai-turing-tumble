"""
GUI for Connect Four
"""

# standard library imports
import time
from typing import Optional
import sys

# 3rd party imports
import gym
import numpy as np
import PySimpleGUI as sg
import ray.rllib.agents.ppo as ppo
# noinspection PyPackageRequirements
import torch
import ray
from ray.rllib.utils.typing import EnvType

# local imports (i.e. our own code)
from connect_four.helpers import determine_color, get_game_mode, invert_board, restore_agents, return_layout, \
    get_latest_agent_checkpoint
# noinspection PyUnresolvedReferences
from utilities import utilities, registration


class ConnectFourGUI:
    """
    This class implements the GUI for the Connect Four game.
    """

    agent = None
    env = None
    render_mode: str = None

    def __init__(
            self,
            environment: EnvType,
            game_mode: Optional[int] = 1,
            agent1=None,
            agent2=None
    ):
        """
        Initializes the GUI for the Connect Four game.

        :param environment: the connect four environment
        :param game_mode: the game mode the GUI is started with
        :param agent1: the first agent
        :param agent2: the second agent
        """
        self.env = environment
        self.agent1 = agent1
        self.agent2 = agent2

        print(f"game_mode: {game_mode}")
        if game_mode == 2 and not agent1:
            sys.exit("no agent passed")
        elif game_mode == 3 and not agent1 or not agent2:
            sys.exit("either agent1 or agent2 missing")
        if game_mode == 0:
            self.greedy()
        if game_mode == 1:
            self.ai()
        elif game_mode == 2:
            self.ai_vs_ai()
        elif game_mode == 3:
            self.ai_vs_greedy()
        elif game_mode == 4:
            self.greedy_vs_greedy()

    def _update_layout(self, window):
        """
        Call to update layout

        :param window: PySimpleGUI window
        :return: None
        """
        for i in range(len(self.env.state)):
            for j in range(len(self.env.state[0])):
                window[f'{i},{j}'].update(background_color=determine_color((i, j), self.env.state))

    def greedy(self):
        """
        Starts a GUI game against the greedy agent

        :return: None
        """
        layout = return_layout(env_state=self.env.state)

        window = sg.Window(
            'ConnectFour',
            layout=layout,
            font="Helvetica",
            background_color="white"
        )
        while True:
            event, values = window.read()

            player_action = int(event) - 1
            print(f"player_action is: {player_action}")
            self.env.state, reward, self.env.done, info = self.env.interactive_step(
                player_action, agent_id=1)
            self._update_layout(window)

            if self.env.done:
                self._update_layout(window)
                break
            self.env.state, reward, self.env.done, info = self.env.interactive_step(
                self.env.get_greedy_action(2), agent_id=2)
            self._update_layout(window)
            if self.env.done:
                self._update_layout(window)
                break
        window.read(timeout=5000)
        window.close()

        window.close()

    def greedy_vs_greedy(self):
        """
        Starts a game where the greedy agent plays against another greedy agent

        :return: None
        """
        layout = return_layout(env_state=self.env.state)
        window = sg.Window(
            'ConnectFour',
            layout=layout,
            font="Helvetica",
            background_color="white"
        )
        while True:
            window.read(timeout=1000)

            self.env.state, reward, self.env.done, info = self.env.interactive_step(
                self.env.get_greedy_action(1), agent_id=1)
            self._update_layout(window)

            if self.env.done:
                self._update_layout(window)

            self.env.state, reward, self.env.done, info = self.env.interactive_step(
                self.env.get_greedy_action(2), agent_id=2)
            self._update_layout(window)
            if self.env.done:
                self._update_layout(window)

                break
        window.read(timeout=5000)
        window.close()

        window.close()

    def ai(self):
        """
        Starts the GUI game human vs AI

        :return: None
        """
        layout = return_layout(env_state=self.env.state)

        window = sg.Window(
            'ConnectFour',
            layout=layout,
            font="Helvetica",
            background_color="white"
        )
        while True:
            event, values = window.read()
            player_action = int(event) - 1
            print(f"player_action is: {player_action}")
            self.env.connectfour.placeToken(player_action, 2)
            self.env.state = self.env.connectfour.getState()

            self._update_layout(window)
            if self.env.done:
                self._update_layout(window)
                break

            agent_action = self.agent1.compute_action(invert_board(self.env.state))

            self.env.state, reward, self.env.done, self.env.info = self.env.connectfour.interactive_step(agent_action)
            self.env.state = np.array(self.env.state)
            self.env.done = bool(self.env.done)
            self.env.info = {}

            # self.env.reward += int(reward)

            self._update_layout(window)

            if self.env.done:
                self._update_layout(window)
                break
        window.read(timeout=5000)
        window.close()

    def ai_vs_greedy(self):
        """
        Starts a gui game AI vs greedy.

        :return: None
        """
        layout = return_layout(env_state=self.env.state)

        window = sg.Window(
            'ConnectFour',
            layout=layout,
            font="Helvetica",
            background_color="white"
        )
        player = True
        while True:
            window.read(timeout=1000)
            if player:
                self._update_layout(window)
                agent_1_action = self.agent1.compute_action(self.env.state)

                self.env.state, reward, self.env.done, self.env.info = self.env.interactive_step(agent_1_action,
                                                                                                 1)
            else:
                window.read(timeout=2000)
                self.env.state, reward, self.env.done, info = self.env.interactive_step(
                    self.env.get_greedy_action(2), agent_id=2)
            self._update_layout(window)
            player = not player
            if self.env.done:
                self._update_layout(window)
                self.env.reset()
                break

        window.read(timeout=5000)
        window.close()

        window.close()

    def ai_vs_ai(self):
        """
        Starts a gui game AI vs AI.

        :return: None
        """
        layout = return_layout(env_state=self.env.state)
        window = sg.Window(
            'ConnectFour',
            layout=layout,
            font="Helvetica",
            background_color="white"
        )
        player = True
        while True:
            window.read(timeout=500)
            self._update_layout(window)
            if player:
                agent_1_action = self.agent1.compute_action(self.env.state)
                self.env.state, reward, self.env.done, self.env.info = self.env.interactive_step(agent_1_action,
                                                                                                 1)
                self.env.state = np.array(self.env.state)
                self.env.done = bool(self.env.done)
                self.env.info = {}
                self._update_layout(window)
            elif not player:
                agent_2_action = self.agent2.compute_action(invert_board(self.env.state))
                self.env.state, reward, self.env.done, self.env.info = self.env.interactive_step(agent_2_action,
                                                                                                 2)
                self.env.state = np.array(self.env.state)
                self.env.done = bool(self.env.done)
                self.env.info = {}
                self._update_layout(window)

            if self.env.done:
                self._update_layout(window)
                break
            player = not player

        window.read(timeout=5000)
        window.close()

        window.close()

    def console_no_interaction(self):
        """
        Starts the ConnectFour game without interaction in the console.

        :return: None
        """

        def _print_game():
            n, _ = np.array(self.env.state).shape
            print("==============================")
            print(" 1  2  3  4  5  6  7")
            for i in range(n):
                row = self.env.state[i].copy()
                row = [" -" if x == 0 else x for x in row]
                row = [" X" if x == 1 else x for x in row]
                row = [" O" if x == 2 else x for x in row]

                print(*row)
                print()
            print("==============================")

        while not self.env.done:
            action = self.agent1.compute_single_action(self.env.state)
            self.env.state, reward, self.env.done, self.env.info = self.env.step(action)
            self.env.reward += reward
            _print_game()
            time.sleep(1)

        time.sleep(3)


def start_game():
    """
    Starts the ConnectFour game.

    :return: None
    """
    ray.init(local_mode=True)

    trainer_config = ppo.DEFAULT_CONFIG.copy()
    trainer_config["framework"] = "torch"
    trainer_config["model"] = {
        "custom_model": "custom_torch_fcnn",
        "custom_model_config": {
            "fcnet_hiddens": [256, 256, 256],
            "fcnet_activation": torch.nn.ReLU,
            "no_final_layer": False,
            "vf_share_layers": False,
            "free_log_std": False
        },
    }
    env = gym.make("connectfour-v0")

    agents = restore_agents([get_latest_agent_checkpoint(), get_latest_agent_checkpoint()], trainer_config)

    ConnectFourGUI(env, get_game_mode(), agent1=agents[0], agent2=agents[1])


if __name__ == "__main__":
    start_game()
