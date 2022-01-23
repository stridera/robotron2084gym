# -*- coding: utf-8 -*-
"""
Robotron 2084 Game Module

Provides a way to play the Robotron 2084 game one frame at a time.

Goal:
    This is an attempt to create Robotron 2084 for reinforcement learning models.
    It attempts to follow the OpenAI Gym (https://gym.openai.com/) protocol for
    easy implementation.  The end goal is to create a model that will play
    the xbox 360 version on the actual hardware.

    See https://github.com/stridera/robotron for my reinforcement learning progress.

Example:
    >>> from robotron import Robotron
    >>>

"""
from typing import Tuple
import numpy as np
import cv2
import gym

from .engine import Engine
from .utils import crop


class RobotronEnv(gym.Env):
    """
    The Robotron 2084 Environment.
    """

    FAMILY_REWARD = 10.0

    def __init__(self, level: int = 1, fps: int = 30, godmode: bool = False, always_move: bool = False, headless: bool = True):
        """
        Setup the environment

        args:
            level (int): What level to start at.  Default: 1
            fps (int): Frames per secont to run at.  Default: 30
            return_en
            godmode (bool): Are you a god? (Can't die.) Default: False
            always_move (bool): Always move/shoot.  Drops action space from 9x9 to 8x8  Default: False
            headless (bool): Skip creating the screen.
        """
        self.engine = Engine(level, fps, godmode, headless)
        self.action_mod = 1 if always_move else 0
        self.score = 0
        width, height = self.engine.play_rect.size
        play_area = (height, width, 3)

        # Gym Requirements
        actions = 8 if always_move else 9
        self.action_space = gym.spaces.MultiDiscrete([actions, actions])
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=play_area, dtype=np.uint8)
        self.metadata = {'render.modes': ['human', 'rgb_array']}

    def reset(self):
        """
        Reset the game and get an initial observation

        returns:
            np.ndarray: The initial obs
        """
        self.score = 0
        return self.get_state(self.engine.reset())

    def step(self,  action: Tuple[int, int]) -> Tuple[np.ndarray, int, bool, dict]:
        r"""
        Play one frame of the game.  We return the obs, reward, done, and
        any additional info.  Follows the openai gym observations structure.
        https://gym.openai.com/docs/#observations

        args:
            action (Tuple[int, int]): The inputs to the game. This consists of two ints between 0-8
            following the cardinal points of the joystick.

                8   1   2
                  \ | /
                7 - 0 - 3
                  / | \
                6   5   4

            If we have always_move set to True, we drop the Noop action. (Basically add 1 to each action)

        returns:
            (np.ndarray, float, bool, dict): the obs, reward, done, and info

        raises:
            ValueError: Raised if input is invalid.
        """
        move, shoot = action

        if not 0 <= move <= 9 - self.action_mod or not 0 <= shoot <= 9 - self.action_mod:
            raise ValueError("Invalid Action")

        self.engine.handle_input(move + self.action_mod, shoot + self.action_mod)
        (image, score, lives, level, dead) = self.engine.update()

        reward = (self.engine.score - self.score) / 100.0
        self.score = self.engine.score

        return self.get_state(image), reward, dead, {
            'score': score,
            'level': level,
            'lives': lives,
            'family': self.engine.family_remaining(),
            'data': self.engine.get_enemy_data(),
        }

    def get_state(self, image):
        """
        Convert the image into a 84 by 84 pixel image in a format for deep learning agents to easily consume.

        returns:
            np.ndarray: The game image for the current step
        """
        image = crop(image, self.engine.play_area)
        # cv2.imshow('image', image)
        # cv2.waitKey(0)
        # image = cv2.resize(image, (84, 84), interpolation=cv2.INTER_LINEAR)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def render(self, mode):
        """ TODO:  Render the game on the screen while playing. """
        image = self.engine.get_image()
        if mode == 'human':
            return image
        else:
            return self.get_state(image)
