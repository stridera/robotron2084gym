"""Robotron 2084 Gymnasium Environment"""
from gymnasium.envs.registration import register

from .robotron import RobotronEnv

register(
    id="Robotron-v0",
    entry_point="robotron:RobotronEnv",
    max_episode_steps=None,  # No default time limit (users can set via wrapper or kwarg)
)
