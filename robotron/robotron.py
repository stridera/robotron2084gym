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

    def __init__(self, level: int = 1, fps: int = 30, godmode: bool = False, headless: bool = True):
        """
        Setup the environment

        args:
            level (int): What level to start at.  Default: 1
            fps (int): Frames per secont to run at.  Default: 30
            godmode (bool): Can the player die?  Default: False
            headless (bool): Skip creating the screen.
        """
        self.engine = Engine(level, fps, godmode, headless)
        self.score = 0
        width, height = self.engine.play_rect.size
        play_area = (height, width, 3)

        # Gym Requirements
        self.action_space = gym.spaces.Discrete(81)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=play_area, dtype=np.uint8)

    def reset(self):
        """
        Reset the game and get an initial observation

        returns:
            np.ndarray: The initial obs
        """
        self.score = 0
        return self.get_state(self.engine.reset())

    def step(self,  action: int) -> Tuple[np.ndarray, int, bool, dict]:
        r"""
        Play one frame of the game.  We return the obs, reward, done, and
        any additional info.  Follows the openai gym observations structure.
        https://gym.openai.com/docs/#observations

        args:
            action (int): The inputs to the game.  The expected input should
            be between 0 and 81 (9*9).  This consists of two ints between 0-8
            following the cardinal points of the joystick.

                8   1   2
                  \ | /
                7 - 0 - 3
                  / | \
                6   5   4

            Final equation should be `action = left * 9 + right`

            Consider moving to bits?  `action = left << 4 | right`

        returns:
            (np.ndarray, float, bool, dict): the obs, reward, done, and info

        raises:
            ValueError: Raised if input is invalid.
        """
        if not 0 <= action <= 81:
            raise ValueError("Invalid Action")

        move = action // 9
        shoot = action % 9
        self.engine.handle_input(move, shoot)
        (image, score, lives, level, dead) = self.engine.update()

        reward = (self.engine.score - self.score) / 100.0
        self.score = self.engine.score

        return self.get_state(image), reward, dead or level > 1, {
            'score': score,
            'level': level,
            'lives': lives
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

    def render(self):
        """ TODO:  Render the game on the screen while playing. """
