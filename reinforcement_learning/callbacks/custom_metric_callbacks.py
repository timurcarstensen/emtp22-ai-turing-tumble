"""
This file implements some of the functions that are defined in RLLib's DefaultCallbacks.
"""

# standard library imports
from typing import Dict, TYPE_CHECKING

# 3rd party imports
from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.evaluation import RolloutWorker
from ray.rllib.env.base_env import BaseEnv
from ray.rllib.policy import Policy
from ray.rllib.evaluation.episode import Episode
from ray.rllib.utils.typing import PolicyID
# noinspection PyPackageRequirements
import torch

if TYPE_CHECKING:
    from ray.rllib.agents.trainer import Trainer
    from ray.rllib.evaluation import RolloutWorker


class CustomMetricCallbacks(DefaultCallbacks):

    def on_episode_start(
            self,
            *,
            worker: RolloutWorker,
            base_env: BaseEnv,
            policies: Dict[str, Policy],
            episode: Episode,
            **kwargs
    ) -> None:
        """
        Callback run at the start of each episode.

        :param worker: Rollout worker of ray
        :param base_env: the base environment
        :param policies: policies of the agent
        :param episode: the episode
        :param kwargs: other arguments
        :return: None
        """
        # Make sure this episode has just been started (only initial obs
        # logged so far).
        assert episode.length == 0, (
            "ERROR: `on_episode_start()` callback should be called right "
            "after env reset!"
        )
        episode.user_data["game_history"] = []

    def on_trainer_init(
            self,
            *,
            trainer: "Trainer",
            **kwargs,
    ) -> None:
        """
        Callback run when a new trainer instance has finished setup.
        This method gets called at the end of Trainer.setup() after all
        the initialisation is done, and before actually training starts.

        :param trainer: reference to the trainer
        :param kwargs: other arguments
        :return: None
        """
        if trainer.config["env_config"]["pretraining"]:
            trainer.get_policy().model.load_state_dict(
                torch.load(trainer.config["env_config"]["pretrained_model_path"]))

    def on_episode_end(
            self,
            *,
            worker: "RolloutWorker",
            base_env: BaseEnv,
            policies: Dict[PolicyID, Policy],
            episode: Episode,
            **kwargs,
    ) -> None:
        """
        Is called at the end of each episode. Appends the game history to the episode user data.

        :param worker: Rollout worker of ray
        :param base_env: the base environment
        :param policies: policies of the agent
        :param episode: the episode
        :param kwargs: other arguments
        :return: None
        """
        # Check if there are multiple episodes in a batch, i.e.
        # "batch_mode": "truncate_episodes".
        if worker.policy_config["batch_mode"] == "truncate_episodes":
            # Make sure this episode is really done.
            assert episode.batch_builder.policy_collectors["default_policy"].batches[
                -1
            ]["dones"][-1], (
                "ERROR: `on_episode_end()` should only be called "
                "after episode is done!"
            )

        info = episode.last_info_for()
        episode.user_data["game_history"].append(info["won"])
        episode.custom_metrics["game_history"] = episode.user_data["game_history"][0]
        episode.hist_data["game_histories"] = episode.user_data["game_history"]

    def on_train_result(
            self,
            *,
            trainer: "Trainer",
            result: dict,
            **kwargs
    ) -> None:
        """
        This function is called after the trainer has finished training one epoch.

        :param trainer: reference to the trainer
        :param result: train result
        :param kwargs: other arguments
        :return: None
        """
        if result["custom_metrics"]["game_history_mean"] > 0.85:
            print("incrementing phase")
            trainer.workers.foreach_worker(
                lambda ev: ev.foreach_env(
                    lambda env: env.increment_phase()))
