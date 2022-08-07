"""
Contains helper functions for the connect four module.
"""

# standard library imports
from typing import List
import sys
import os

# 3rd party imports
import numpy as np
# noinspection PyPep8Naming
import PySimpleGUI as sg
from ray.rllib.agents.ppo.ppo import PPOTrainer
# noinspection PyPackageRequirements
import torch
import ray.rllib.agents.ppo as ppo


# functions
def get_config() -> dict:
    """
    Returns the config for the PPO agent with the necessary settings for the connect four environment

    :return: dictionary containing the config
    """
    config = ppo.DEFAULT_CONFIG.copy()
    config["framework"] = "torch"
    config["model"] = {
        "custom_model": "custom_torch_fcnn",
        "custom_model_config": {
            "fcnet_hiddens": [256, 256, 256],
            "fcnet_activation": torch.nn.ReLU,
            "no_final_layer": False,
            "vf_share_layers": False,
            "free_log_std": False
        },
    }

    return config


def return_layout(env_state) -> list:
    """
    Returns the layout of the board.

    :param env_state: state of the connect four environment
    :return: list describing the layout
    """
    return [
        [
            [
                sg.Text(
                    size=(7, 4), justification="center",
                    background_color=determine_color((row, col), env_state),
                    border_width=1,
                    key=f"{row},{col}")
                for col in range(7)
            ]
            for row in range(6)
        ], [
            [
                sg.Button(
                    f"{col + 1}",
                    size=(6, 1),
                    button_color="#343864",
                    mouseover_colors="#ed5853"
                )
                for col in range(7)
            ]
        ]
    ]


def determine_color(coordinates: tuple, board: List[List]) -> str:
    """
    Determines the colour of a piece at a given coordinate.

    :param coordinates: the coordinates of the piece
    :param board: the board
    :return: the colour of the piece
    """
    if board[coordinates[0]][coordinates[1]] == 0:
        return "white"
    if board[coordinates[0]][coordinates[1]] == 1:
        return "#ed5853"
    else:
        return "#343864"


def get_game_mode():
    """
    Gets the game mode from the console.

    :return: game_mode
    """
    game_modes = {
        "--humanvsgreedy": 0,
        "--humanvsai": 1,
        "--aivsai": 2,
        "--aivsgreedy": 3,
        "--greedyvsgreedy": 4
    }
    args = sys.argv[1:]
    if len(args) < 1:
        print("No argument found")
        sys.exit(0)
    if args[0] not in game_modes.keys():
        print('This game mode does not exist')
        sys.exit(0)
    return game_modes[args[0]]


def get_paths(game_mode: int):
    """
    Returns the paths necessary to start the agents for Ai vs Human or AI vs AI (must be absolute paths)

    :param game_mode: int
    """
    agent_path1 = None
    agent_path2 = None
    if game_mode >= 2:
        agent_path1 = input("Agent game path: ")
    if game_mode >= 3:
        agent_path2 = input("Agent game path: ")
    if game_mode == 0:
        agent_path1 = input("Agent game path: ")
    return [agent_path1, agent_path2]


def cast_to_np_array(conv):
    """
    Converts an array to np array

    :param conv: int
    :return: np_array
    """
    helper_array = [[0] * 7 for i in range(6)]
    for i in range(6):
        for j in range(7):
            helper_array[i][j] = conv[i][j]
    return np.array(helper_array, dtype=np.float32)


def invert_board(board: np.ndarray):
    """
    Player 1 gets inverted to player 2, player 2 to player 1

    :param board: np.array
    :return: np.array
    """
    tmp = cast_to_np_array(board)
    b1 = tmp.copy()
    b1 = np.where(b1 == 1, 3, b1)
    b1 = np.where(b1 == 2, 1, b1)
    return np.where(b1 == 3, 2, b1)


def restore_agents(paths, config):
    """
    Gets agents from multiple paths

    :param paths: string[]
    :param config:
    :return: agents[]
    """
    agent1 = PPOTrainer(env="connectfour-v0", config=config)
    agent2 = PPOTrainer(env="connectfour-v0", config=config)
    if paths[0]:
        agent1.restore(paths[0])
    if paths[1]:
        agent1.restore(paths[1])
    return [agent1, agent2]


def preprocess_results(result: dict) -> dict:
    """
    Removes the Observation space from the training result dictionary returned
    by agent.train() since it could not be serialised by wandb

    :param result: dictionary of type rllib.agent.train()
    :return: modified input dict
    """
    result["config"]["multiagent"].pop("policies", None)
    result["config"]["evaluation_config"]["multiagent"].pop("policies", None)
    return result


def get_latest_agent_checkpoint():
    """
    Gets the latest checkpoint of the agent

    :return: latest agent checkpoint from data/agent_checkpoints/connect_four
    """
    agent_checkpoints = os.listdir(f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/agent_checkpoints/connect_four")
    agent_checkpoints.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    return f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/agent_checkpoints/connect_four/{agent_checkpoints[-1]}" \
           f"/checkpoint-{agent_checkpoints[-1].split('_')[1].lstrip('0')}"
