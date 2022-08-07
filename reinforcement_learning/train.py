"""
Training file for the BugBit environment.
"""

# standard library imports
import os

# 3rd party imports
import torch
import ray
from ray.tune.integration.wandb import WandbLoggerCallback
from ray import tune
from ray.tune.schedulers import ASHAScheduler
import pandas as pd

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities
# noinspection PyUnresolvedReferences
from utilities import registration
from callbacks.custom_metric_callbacks import CustomMetricCallbacks

# training set path and pretrained_model_path must point to the respective files in the data directory

num_bugs: int = 3
sample_size = int((2 ** num_bugs) / 2)
rl_training_set_file_name: str = ""
pretrained_model_file_name: str = ""

global_config = {
    "training_set_path": f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/rl_training_sets/"
                         f"{rl_training_set_file_name}",
    "pretraining": True,
    "pretrained_model_path": f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/model_weights"
                             f"/{pretrained_model_file_name}",
}

if not rl_training_set_file_name or (global_config["pretraining"] and not pretrained_model_file_name):
    raise ValueError("rl_training_set_file_name and/or pretrained_model_path must be set")

if __name__ == "__main__":
    # load training set from pickle
    training_set = pd.read_pickle(global_config["training_set_path"])

    # initialise ray (set local_mode to True for debugging)
    ray.init()

    # running the experiment
    tune.run(
        "PPO",
        verbose=0,  # verbosity of the console output during training
        # checkpointing settings
        checkpoint_freq=5,  # after every 5 epochs, a checkpoint is created
        local_dir=f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/agent_checkpoints/bugbit",
        checkpoint_score_attr="custom_metrics/game_history_mean",
        keep_checkpoints_num=1,  # how many checkpoints to keep in the end
        num_samples=1,  # number of simultaeous agents to train
        scheduler=ASHAScheduler(
            metric="custom_metrics/game_history_mean",
            time_attr="training_iteration",
            mode="max",
            max_t=81,
            reduction_factor=3,
            brackets=1
        ),  # scheduler for training (i.e. predictive termination)
        callbacks=[
            # adjust the entries here to conform to your wandb environment
            # cf. https://docs.wandb.ai/ and https://docs.ray.io/en/master/tune/examples/tune-wandb.html
            WandbLoggerCallback(
                api_key_file="wandb_key_file",
                project="ray-tune-bugbit",
                entity="mtp-ai-board-game-engine",
                group="final-submission-testing",
            ),
        ],
        # trainer config
        config={
            "callbacks": CustomMetricCallbacks,
            "num_envs_per_worker": 1,  # how many environments to run in parallel per worker (read: CPU thread)
            "num_workers": 1,  # how many CPU threads are used for training one agent
            "framework": "torch",  # framework to use for training (i.e. PyTorch or TensorFlow)
            "env": "bugbit-v0",  # name of the environment which is used for training
            # config of the neural network
            # if pretraining=True: the pretrained model is used for initialisation and hence must have the same config
            # as below. Else: the model is initialised with random weights and one can modify the model config as needed.
            "model": {
                "custom_model": "custom_torch_fcnn",
                "custom_model_config": {
                    "fcnet_hiddens": [256, 256, 256],
                    "fcnet_activation": torch.nn.ReLU,
                    "no_final_layer": False,
                    "vf_share_layers": False,
                    "free_log_std": False,
                    "pretraining": global_config["pretraining"],
                    "pretrained_model_path": global_config["pretrained_model_path"],
                },
            },
            # bugbit gym environment config
            "env_config": {
                "n_bugs": num_bugs,  # number of bugs
                "training_set": training_set,
                "max_steps": 3,  # the maximum number of steps before the game is terminated
                "sample_size": sample_size,  # MUST be set to (n_bugs^2)/2
                "pretraining": global_config["pretraining"],
                "pretrained_model_path": global_config["pretrained_model_path"],
            }
        },
    )
