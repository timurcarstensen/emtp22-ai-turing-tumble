"""
This file is a helper file which just registers our custom environments and models with the ray registry.
"""

# 3rd party imports
from ray.tune.registry import register_env
from ray.rllib.models import ModelCatalog

# local imports (i.e. our own code)
from custom_torch_models.rl_fully_connected_network import FullyConnectedNetwork
from environments.envs.bugbit_env import BugBit
from environments.envs.connectfourmvc_env import ConnectFourMVC


# registering the BugBit environment
def bugbit_env_creator(env_config):
    return BugBit(env_config)


register_env("bugbit-v0", bugbit_env_creator)


# registering the ConnectFour environment
def connect_four_env_creator(env_config):
    return ConnectFourMVC()


register_env("connectfour-v0", connect_four_env_creator)

# registering the custom fully connected network model
ModelCatalog.register_custom_model("custom_torch_fcnn", FullyConnectedNetwork)
