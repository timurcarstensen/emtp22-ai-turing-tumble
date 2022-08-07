from gym.envs.registration import register

register(
    id="bugbit-v0",
    entry_point="environments.envs:BugBit_v0",
)

register(
    id="connectfour-v0",
    entry_point="environments.envs:ConnectFourMVC",
)