"""
Training file for connect four.
"""

# standard library imports
import shutil
import os

# 3rd party imports
import ray
import ray.rllib.agents.ppo as ppo
import wandb

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities
# noinspection PyUnresolvedReferences
from utilities import registration
import connect_four.helpers as helpers

wandb.login()
wandb.init(project="connect-four", entity="mtp-ai-board-game-engine")


def main():
    """
    Main training function for connect four.
    
    :return: None
    """
    # init directory in which to save checkpoints
    chkpt_root = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/agent_checkpoints/connect_four"
    shutil.rmtree(chkpt_root, ignore_errors=True, onerror=None)

    # init directory in which to log results
    ray_results = "{}/ray_results/".format(os.getenv("HOME"))
    shutil.rmtree(ray_results, ignore_errors=True, onerror=None)

    # start Ray -- add `local_mode=True` here for debugging
    ray.init()

    # configure the environment and create agent
    config = helpers.get_config()
    config["num_gpus"] = 0
    config["num_workers"] = 4

    agent = ppo.PPOTrainer(env="connectfour-v0", config=config)

    # change the number of iterations to train for in range()
    for n in range(100):
        result = agent.train()
        helpers.preprocess_results(result)
        wandb.log(result)
        agent.save(chkpt_root)

        print(
            f"ITERATION {n + 1:2d}, "
            f"min: {result['episode_reward_min']:8.2f}, "
            f"mean: {result['episode_reward_mean']:8.2f}, "
            f"max: {result['episode_reward_max']:8.2f}, "
            f"mean length: {result['episode_len_mean']:8.2f} "
        )


# running this file will train a PPO agent and save the checkpoints in the
# data/agent_checkpoints/connect_four directory
if __name__ == "__main__":
    main()
