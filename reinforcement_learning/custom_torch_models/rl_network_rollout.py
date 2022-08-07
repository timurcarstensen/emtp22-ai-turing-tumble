"""
This class is used for performing a rollout on the fully connect reinforcement learning network that has
been pretrained.
"""

# standard library imports
import warnings
import sys
import random
import copy
import os
from typing import Optional, List

# 3rd party imports
import numpy as np
import gym
import torch

# local imports
from dataset_generators.utils import cf_to_lower_triangular_flattened, flattened_repr_to_control_flow_matrix
from dataset_generators.pretraining_dataset_generation import read_samples, read_programs
from custom_torch_models.rl_fully_connected_network import FullyConnectedNetwork

warnings.filterwarnings("ignore", category=UserWarning)
torch.set_printoptions(threshold=sys.maxsize)


def rollout(
        model: torch.nn.Module,
        x_test: torch.Tensor,
        t_test: torch.Tensor,
        num_bugs: int,
        play_out_indices: List[int],
        zero_rollout: Optional[bool] = False
):
    """
    This method performs a rollout on the given model. The network is given a set of test samples for which it has 50
    epochs to take actions that reach a target CF-Matrix state. Each step is printed to the console.

    :param model: The pretrained pytorch network
    :param x_test: Testing data (CF-Matrix, Input-Output samples)
    :param t_test: Target cf matrices
    :param num_bugs: Number of bugs
    :param play_out_indices: Indices defining which test data to roll out
    :param zero_rollout: True, if you want to start with an empty CF matrix.
    :return: None
    """
    successes = 0
    for pi in range(len(play_out_indices)):

        index = play_out_indices[pi]
        rand_sample = copy.deepcopy(x_test[index])
        if torch.cuda.is_available():
            rand_sample = rand_sample.cpu()
        current_matrix = copy.deepcopy(rand_sample[
                                       :num_bugs * (
                                               num_bugs - 1)])  # np.zeros(shape=(num_bugs * (num_bugs - 1)))
        rand_sample = rand_sample[num_bugs * (num_bugs - 1):]
        if zero_rollout:
            current_matrix = np.zeros(shape=current_matrix.shape)

        current_input = np.concatenate((current_matrix, rand_sample))

        io_size = len(rand_sample)
        inputs = rand_sample[:io_size // 2].numpy()
        outputs = rand_sample[-io_size // 2:].numpy()

        inputs = np.reshape(inputs, newshape=(-1, num_bugs))
        outputs = np.reshape(outputs, newshape=(-1, num_bugs))

        actions = 0

        print("\n")
        print("New Function with following IN-Out-Samples:")
        print("Inputs\t\t\t\t\tOutputs")
        for io in range(len(inputs)):
            print(inputs[io], "\t", outputs[io])

        print("\nTarget Matrix:")
        if torch.cuda.is_available():
            t2 = torch.from_numpy(cf_to_lower_triangular_flattened(t_test[index].cpu())).float()
            print(t_test[index].cpu())
        else:
            t2 = torch.from_numpy(cf_to_lower_triangular_flattened(t_test[index])).float()
            print(t_test[index])

        for step in range(50):
            print("\n")
            print(f"Input-Matrix at Step {step}:")
            print(flattened_repr_to_control_flow_matrix(current_matrix, num_bugs))

            current_input = torch.from_numpy(current_input).float()

            if torch.cuda.is_available():
                out = model.custom_forward(current_input.cuda())
                out_choice = torch.argmax(out)
                # if epoch == 0:

                t1 = current_input[:num_bugs * (num_bugs - 1)]

            else:
                out = model.custom_forward(current_input)
                out_choice = torch.argmax(out)
                t1 = current_input[:num_bugs * (num_bugs - 1)]

                t2 = torch.from_numpy(cf_to_lower_triangular_flattened(t_test[index])).float()

            print(f"Action chosen: {out_choice.item()}\n\n")
            if torch.equal(t1, t2):
                successes += 1
                # steps_correct.append(actions)
                break

            current_matrix[out_choice] = 1 if current_matrix[out_choice] == 0 else 0
            actions += 1
            current_input = np.concatenate((current_matrix, rand_sample))

        print("----------------------")
        print("----------------------")
    print(f"Solved {successes}/{len(play_out_indices)} Challenges.")


def start_rollout(
        n_bugs: int,
        multiple_actions: bool,
        model_path: str,
        n_rollouts: Optional[int] = 10,
        zero_rollout: Optional[bool] = False,
        config: Optional[dict] = None
):
    """
    This method starts a rollout on the given model.

    :param n_bugs: number of bugs
    :param multiple_actions: if True, the algorithm can take one of multiple delete actions in a single step.
    :param model_path: Absolute path to the model that is used for the rollout
    :param n_rollouts: Number of rollouts
    :param zero_rollout: if true, start each rollout with an empty CF matrix
    :param config: config dictionary for the custom_torch_fcnn
    :return: None
    """
    random.seed(10)

    num_outputs = (2 * n_bugs ** 2) // 2 - n_bugs

    if not config:
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

    observation_space = gym.spaces.Box(
        low=0,
        high=2,
        shape=(1, (2 * n_bugs ** 2) // 2 - n_bugs + (2 ** n_bugs // 2) * 2 * n_bugs)
    )

    action_space = gym.spaces.Discrete(((2 * n_bugs ** 2) // 2 - n_bugs))
    net = FullyConnectedNetwork(obs_space=observation_space, action_space=action_space, num_outputs=num_outputs,
                                model_config=config, name="default_model")

    x, y = read_samples(n_bugs, multiple_actions=multiple_actions)
    t = read_programs(n_bugs, multiple_actions=multiple_actions)

    test_indices = random.sample(range(0, len(x)), int(len(x) * 0.2))
    x_test = np.take(x, test_indices, axis=0)
    y_test = np.take(y, test_indices, axis=0)
    t_test = np.take(t, test_indices, axis=0)

    x = np.delete(x, test_indices, axis=0)
    x = torch.from_numpy(x).float()
    x_test = torch.from_numpy(x_test).float()
    y_test = torch.from_numpy(y_test).float()

    # load network
    net.load_state_dict(torch.load(model_path))

    play_out_indices = random.sample(range(len(x_test)), n_rollouts)
    rollout(net, x_test, t_test, num_bugs=n_bugs, play_out_indices=play_out_indices, zero_rollout=zero_rollout)


if __name__ == "__main__":
    random.seed(10)

    model_file_name: str = "RL_Pretraining_Model_KL_DIV_Training_3-Bugs--lr=0.001--batch_size=100" \
                           "--Multiple_Actions=TrueFalseDisjoint_Functions=False"

    if not model_file_name:
        raise ValueError("No model file name given.")

    # start a rollout with n_bugs for the given model in model_path
    start_rollout(
        n_bugs=3,
        model_path=f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/model_weights/{model_file_name}",
        multiple_actions=True,
        zero_rollout=False,
    )
