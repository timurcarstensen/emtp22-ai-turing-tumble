"""
The neural network we wish to use instead of the default network provided by ray's PPO trainer.
"""

# standard library imports
import os
import sys
import random
import copy
import logging
import warnings
from typing import Optional

# 3rd party imports
import numpy as np
import gym
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.models.torch.misc import SlimFC, AppendBiasLayer, normc_initializer
from ray.rllib.utils.annotations import override
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.typing import Dict, TensorType, List, ModelConfigDict
import wandb
import torch

from torch.utils.data import DataLoader
from tqdm import tqdm

# local imports
from dataset_generators.utils import cf_to_lower_triangular_flattened
from dataset_generators.pretraining_dataset_generation import read_samples, read_programs

np.set_printoptions(threshold=sys.maxsize)
torch.set_printoptions(profile="full")
warnings.filterwarnings("ignore", category=UserWarning)

torch, nn = try_import_torch()

logger = logging.getLogger(__name__)


class FullyConnectedNetwork(TorchModelV2, nn.Module):
    """Generic fully connected network."""

    def __init__(
            self,
            obs_space: gym.spaces.Space,
            action_space: gym.spaces.Space,
            num_outputs: int,
            model_config: ModelConfigDict,
            name: str,
    ):
        """
        Initialises the network.

        :param obs_space: The observation space our agent receives.
        :param action_space: The action space available to our agent.
        :param num_outputs: The number of outputs our network should produce.
        :param model_config: The model configuration.
        :param name: The name of our model.
        """

        # update the config
        model_config.update(model_config["custom_model_config"])
        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name
        )
        nn.Module.__init__(self)

        # define the hidden layers
        hiddens = list(model_config.get("fcnet_hiddens", [])) + list(
            model_config.get("post_fcnet_hiddens", [])
        )
        # define the activation function
        activation = model_config.get("fcnet_activation")
        if not model_config.get("fcnet_hiddens", []):
            activation = model_config.get("post_fcnet_activation")

        # define whether output layer should be linear or not
        no_final_linear = model_config.get("no_final_linear")

        # The PPO Trainer has a value and a policy branch. Defines whether they should use the same hidden layers
        # and only use unique prediction heads in the final output layer (True) or we should build two unique networks
        # who only share the same input (observation space) (False).
        self.vf_share_layers = model_config.get("vf_share_layers")

        # For DiagGaussian action distributions, make the second half of the model
        # outputs floating bias variables instead of state-dependent.
        self.free_log_std = model_config.get("free_log_std")

        # Generate free-floating bias variables for the second half of the outputs.
        if self.free_log_std:
            assert num_outputs % 2 == 0, (
                "num_outputs must be divisible by two",
                num_outputs,
            )
            num_outputs = num_outputs // 2

        # Create the hidden layers.
        layers = []
        prev_layer_size = int(np.product(obs_space.shape))
        self._logits = None

        for size in hiddens[:-1]:
            layers.append(
                SlimFC(
                    in_size=prev_layer_size,
                    out_size=size,
                    initializer=normc_initializer(1.0),
                    activation_fn=activation,
                )
            )
            prev_layer_size = size

        # The last layer is adjusted to be of size num_outputs, but it's a layer with activation.
        if no_final_linear and num_outputs:
            layers.append(
                SlimFC(
                    in_size=prev_layer_size,
                    out_size=num_outputs,
                    initializer=normc_initializer(1.0),
                    activation_fn=activation,
                )
            )
            prev_layer_size = num_outputs

        # Finish the layers with the provided sizes (`hiddens`), plus (iff num_outputs > 0)
        # a last linear layer of size num_outputs.
        else:
            if len(hiddens) > 0:
                layers.append(
                    SlimFC(
                        in_size=prev_layer_size,
                        out_size=hiddens[-1],
                        initializer=normc_initializer(1.0),
                        activation_fn=activation,
                    )
                )
                prev_layer_size = hiddens[-1]
            if num_outputs:
                self._logits = SlimFC(
                    in_size=prev_layer_size,
                    out_size=num_outputs,
                    initializer=normc_initializer(0.01),
                    activation_fn=torch.nn.LogSoftmax
                )
            else:
                self.num_outputs = ([int(np.product(obs_space.shape))] + hiddens[-1:])[
                    -1
                ]

        # Layer to add the log std vars to the state-dependent means.
        if self.free_log_std and self._logits:
            self._append_free_log_std = AppendBiasLayer(num_outputs)

        self._hidden_layers = nn.Sequential(*layers)

        self._value_branch_separate = None
        if not self.vf_share_layers:
            # Build a parallel set of hidden layers for the value net.
            prev_vf_layer_size = int(np.product(obs_space.shape))
            vf_layers = []
            for size in hiddens:
                vf_layers.append(
                    SlimFC(
                        in_size=prev_vf_layer_size,
                        out_size=size,
                        activation_fn=activation,
                        initializer=normc_initializer(1.0),
                    )
                )
                prev_vf_layer_size = size
            self._value_branch_separate = nn.Sequential(*vf_layers)

        self._value_branch = SlimFC(
            in_size=prev_layer_size,
            out_size=1,
            initializer=normc_initializer(0.01),
            activation_fn=None,
        )
        # Holds the current "base" output (before logits layer).
        self._features = None
        # Holds the last input, in case value branch is separate.
        self._last_flat_in = None

        if model_config.get("pretraining"):
            self.load_state_dict(torch.load(model_config.get("pretrained_model_path")))

    @override(TorchModelV2)
    def forward(
            self,
            input_dict: Dict[str, TensorType],
            state: List[TensorType],
            seq_lens: TensorType,
    ) -> (TensorType, List[TensorType]):
        """
        Forward pass of the network.

        :param input_dict: The inputs for the forward pass.
        :param state: list of state tensors
        :param seq_lens: 1d tensor holding input sequence lengths
        :return: The logits produced as a result of the forward pass as well as the state
        """

        obs = input_dict["obs_flat"].float()
        self._last_flat_in = obs.reshape(obs.shape[0], -1)
        self._features = self._hidden_layers(self._last_flat_in)
        logits = self._logits(self._features) if self._logits else self._features
        if self.free_log_std:
            logits = self._append_free_log_std(logits)

        return logits, state

    def custom_forward(self, X):
        """
        A custom forward function for pretraining the network. It is different to the forward function as in pretraining
        there is no state and input dict.

        :param X: Input tensor with training data for the forward pass
        :return: The logits produced as a result of the forward pass
        """
        self._last_flat_in = X
        self._features = self._hidden_layers(self._last_flat_in)
        logits = self._logits(self._features) if self._logits else self._features
        if self.free_log_std:
            logits = self._append_free_log_std(logits)
        return logits

    @override(TorchModelV2)
    def value_function(self) -> TensorType:
        """
        Computes the result of the value branch of the network.

        :return: Result of the value branch.
        """

        assert self._features is not None, "must call forward() first"
        if self._value_branch_separate:
            return self._value_branch(
                self._value_branch_separate(self._last_flat_in)
            ).squeeze(1)
        else:
            return self._value_branch(self._features).squeeze(1)

    def sample_train(
            self,
            x: torch.Tensor,
            y: torch.Tensor,
            x_test: torch.Tensor,
            y_test: torch.Tensor,
            t_test: torch.Tensor,
            num_bugs: Optional[int] = 5,
            zero_rollout: Optional[bool] = False,
            num_epochs: Optional[int] = 50,
            learning_rate: Optional[float] = 0.001,
            batch_size: Optional[int] = 100
    ):
        """
        Train the network on the given data.

        :param x: Training samples.
        :param y: Training labels.
        :param x_test: Test samples.
        :param y_test: Test labels.
        :param t_test: The template programs (the CF Matrix) of the test samples.
        :param num_bugs: Number of bugs we are using for the training.
        :param zero_rollout: Do the rollout with empty CF matrices.
        :param num_epochs: Number of epochs to train for.
        :param learning_rate: Learning rate for the optimiser.
        :param batch_size: Batch size for the optimiser.
        :return: the trained model
        """

        # use a TensorDataset
        dataset = torch.utils.data.TensorDataset(x, y)
        train_loader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True
        )
        losses = []
        test_losses = []

        all_tries = []
        train_accuracy = []
        test_accuracy = []
        successful_solves = []
        average_steps_correct = []

        # sample 100 test samples for the play out/rollout
        play_out_indices = random.sample(range(len(x_test)), 100)

        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        kl_div_loss = torch.nn.KLDivLoss(reduction='batchmean')

        for epoch in range(num_epochs):
            self.train()
            batch_losses = []
            train_batch_accuracies = []
            test_batch_accuracies = []

            # train on each batch
            for batch in train_loader:
                input, output = batch  # .view(batch_size,-1)
                if torch.cuda.is_available():
                    cuda0 = torch.device('cuda:0')
                    input = input.to(cuda0)
                output = self.custom_forward(input)
                y_train = (batch[1])
                loss = kl_div_loss(output, y_train)

                # get the accuracy for the current batch
                for out in range(len(output)):
                    argmax = torch.argmax(output[out])
                    if y_train[out][argmax] > 0:  # some probability mass must be on this index
                        train_batch_accuracies.append(1)
                    else:
                        train_batch_accuracies.append(0)
                batch_losses.append(loss.item())
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

            # start testing
            self.eval()
            with torch.no_grad():

                outs = self.custom_forward(x_test)

                # get the accuracy for the test samples
                for out in range(len(outs)):
                    argmax = torch.argmax(outs[out])

                    if y_test[out][argmax] > 0:
                        test_batch_accuracies.append(1)
                    else:
                        test_batch_accuracies.append(0)

                test_loss = kl_div_loss(outs, y_test)
                test_losses.append(test_loss.item())

                # Test with play outs
                if epoch % 5 == 0:  # each 10 epochs
                    tries = []
                    successes = 0
                    steps_correct = []
                    for pi in tqdm(range(len(play_out_indices))):

                        index = play_out_indices[pi]

                        # get test sample
                        rand_sample = copy.deepcopy(x_test[index])

                        if torch.cuda.is_available():
                            rand_sample = rand_sample.cpu()

                        # get only the cf matrix from the test sample, not the input-output pairs
                        current_matrix = copy.deepcopy(rand_sample[
                                                       :num_bugs * (
                                                               num_bugs - 1)])

                        # rand sample is now only the input-output pairs
                        rand_sample = rand_sample[num_bugs * (num_bugs - 1):]

                        # current matrix is empty, if we use zero rollout
                        if zero_rollout:
                            current_matrix = np.zeros(shape=current_matrix.shape)

                        current_input = np.concatenate((current_matrix, rand_sample))

                        # For 50 epochs let the network take actions and break, if the network
                        # found the correct solution
                        actions = 0
                        for step in range(50):
                            current_input = torch.from_numpy(current_input).float()

                            if torch.cuda.is_available():
                                out = self.custom_forward(current_input.cuda())
                                # take the action which the agent is most confident about
                                out_choice = torch.argmax(out)

                                # get the desired solution to evaluate if the current matrix is already correct
                                t1 = current_input[:num_bugs * (num_bugs - 1)]

                                t2 = torch.from_numpy(cf_to_lower_triangular_flattened(t_test[index].cpu())).float()
                            else:
                                out = self.custom_forward(current_input)
                                # take the action which the agent is most confident about
                                out_choice = torch.argmax(out)

                                # get the desired solution to evaluate if the current matrix is already correct
                                t1 = current_input[:num_bugs * (num_bugs - 1)]

                                t2 = torch.from_numpy(cf_to_lower_triangular_flattened(t_test[index])).float()

                            if torch.equal(t1, t2):
                                successes += 1
                                steps_correct.append(actions)
                                break

                            current_matrix[out_choice] = 1 if current_matrix[out_choice] == 0 else 0
                            actions += 1
                            current_input = np.concatenate((current_matrix, rand_sample))

                        tries.append(actions)

                    all_tries.append(np.mean(tries))
                    average_steps_correct.append(np.mean(steps_correct))
                    print(f"\nActions needed for solved programs: {steps_correct}")
                    successful_solves.append(successes)

            train_accuracy.append(np.mean(train_batch_accuracies))
            test_accuracy.append(np.mean(test_batch_accuracies))
            losses.append(np.mean(batch_losses))
            print(
                f"EPOCH {epoch} \t"
                f"Loss: {losses[-1]} \t"
                f"Train Acc: {train_accuracy[-1]} \t"
                f"Test Acc: {test_accuracy[-1]} \t"
                f"Test Loss: {test_losses[-1]} \t"
                f"All tries: {all_tries[-1]} \t"
                f"Correct Solutions: {successful_solves[-1]} \t"
                f"Average Steps per Correct Solution: {average_steps_correct[-1]}"
            )
            if epoch % 10 == 0:
                print("Tries: ", all_tries[-1])
            wandb.log(
                {
                    # the average loss of the training batches in each epoch
                    "train_loss": losses[-1],

                    # the average loss on the test data
                    "test_loss": test_losses[-1],

                    # percentage of how many actions were chosen correctly in the train data
                    "Train Accuracy": train_accuracy[-1],

                    # percentage of how many actions were chosen correctly in the test data
                    "Test Accuracy": test_accuracy[-1],

                    # average number of steps in the rollout
                    "All_tries": all_tries[-1],

                    # number of solved challenges in the rollout
                    "Correct Solutions": successful_solves[-1],

                    # average number of steps of the correctly solved challenges in the rollout
                    "Avg Steps/solution": average_steps_correct[-1]

                }
            )
        return self
