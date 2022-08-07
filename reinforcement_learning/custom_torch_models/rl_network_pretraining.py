"""
This file can be used to pretrain the reinforcement learning agent.
"""

# standard library imports
import random
import os
from typing import Optional

# 3rd party imports
import numpy as np
import gym
import torch
import wandb

# local imports
from reinforcement_learning.custom_torch_models.rl_fully_connected_network import FullyConnectedNetwork
from dataset_generators.pretraining_dataset_generation import read_samples, read_programs
# noinspection PyUnresolvedReferences
from utilities import utilities


def pretrain_network(
        n_bugs: int,
        multiple_actions: Optional[bool],
        zero_rollout: Optional[bool] = False,
        disjoint_functions: Optional[bool] = False,
        config: Optional[dict] = None,
        num_epochs: Optional[int] = 50,
        test_percentage: Optional[float] = 0.2,
        lr: Optional[float] = 0.001,
        batch_size: Optional[float] = 100
):
    """
    Pretrains the reinforcement learning agent. Before, the **pretraining_dataset_generator** has to be executed
    to create the training set.

    :param n_bugs: number of bugs
    :param multiple_actions: whether we want to use training samples, where more than one delete action is possible.
    :param zero_rollout: True, if you want to start with an empty CF matrix.
    :param disjoint_functions: True, if input-output samples should be disjoint between all training and test samples
    :param config: configuration directory to initialize the network
    :param num_epochs: number of training epochs
    :param test_percentage: percentage of test data in the entire data
    :param lr: learning rate
    :param batch_size: batch size
    :return:
    """
    num_outputs = (2 * n_bugs ** 2) // 2 - n_bugs

    if config is None:
        config = {
            'custom_model': 'custom_torch_fcnn',
            'custom_model_config': {
                'fcnet_hiddens': [256, 256, 256],
                'fcnet_activation': torch.nn.ReLU,
                'no_final_layer': False,
                'vf_share_layers': False,
                'free_log_std': False
            }
        }

    # observation and action space are needed to initialise the network
    observation_space = gym.spaces.Box(low=0, high=2,
                                       shape=(1, (2 * n_bugs ** 2) // 2 - n_bugs + (2 ** n_bugs // 2) * 2 * n_bugs))
    action_space = gym.spaces.Discrete(((2 * n_bugs ** 2) // 2 - n_bugs))
    net = FullyConnectedNetwork(obs_space=observation_space, action_space=action_space, num_outputs=num_outputs,
                                model_config=config, name="default_model")

    # read data and create test samples
    x, y = read_samples(n_bugs, multiple_actions=multiple_actions)
    t = read_programs(n_bugs, multiple_actions=multiple_actions)

    if disjoint_functions:
        # take last 20% of training set
        test_indices = range(int(len(x) * (1 - test_percentage)), len(x))
    else:
        test_indices = random.sample(range(0, len(x)), int(len(x) * test_percentage))
    x_test = np.take(x, test_indices, axis=0)
    y_test = np.take(y, test_indices, axis=0)
    t_test = np.take(t, test_indices, axis=0)

    x = np.delete(x, test_indices, axis=0)
    y = np.delete(y, test_indices, axis=0)
    t = np.delete(t, test_indices, axis=0)
    x = torch.from_numpy(x).float()
    y = torch.from_numpy(y).float()
    x_test = torch.from_numpy(x_test).float()
    y_test = torch.from_numpy(y_test).float()
    t_test = torch.from_numpy(t_test).float()

    print((x_test[0]))
    print(y_test[0])

    print(f"Training Samples: {len(x)}")
    print("Testing Samples: {len(X_test)}")

    # prepare the training
    name = f"RL_Pretraining_Model_KL_DIV_Training_{str(n_bugs)}-Bugs--lr={str(lr)}--batch_size={str(batch_size)}--Multiple_Actions=" \
           f"{str(multiple_actions)}{str(zero_rollout)}Disjoint_Functions={str(disjoint_functions)}"

    print("New Run: ", name)

    print(os.getcwd())
    path = os.getenv('REINFORCEMENT_LEARNING_DIR') + "/data/model_weights/" + name
    print(path)

    wandb.login()
    wandb.init(project="Pretraining", entity="mtp-ai-board-game-engine", name=name)

    if torch.cuda.is_available():
        cuda0 = torch.device('cuda:0')
        x = x.to(cuda0)
        y = y.to(cuda0)
        x_test = x_test.to(cuda0)
        y_test = y_test.to(cuda0)
        t_test = t_test.to(cuda0)

    # pretrain the network
    if torch.cuda.is_available():
        net = net.cuda()
    net.sample_train(x, y, x_test, y_test, t_test, zero_rollout=zero_rollout, num_bugs=n_bugs,
                     num_epochs=num_epochs)

    # save pretrained model
    torch.save(net.state_dict(), path)
    wandb.finish()


if __name__ == "__main__":
    pretrain_network(n_bugs=3, multiple_actions=True)
