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

import gym
import os
import pygame
import numpy as np
import cv2

from typing import Tuple

from . import config
from .engine import Engine
from .utils import crop


class RobotronEnv(gym.Env):
    """
    The Robotron 2084 Environment.
    """
    OUTPUT_SIZE = (168, 168)

    def __init__(self, env_config, level: int = 1, fps: int = 30, godmode: bool = False, headless: bool = True):
        """
        Setup the environment

        args:
            level (int): What level to start at.  Default: 1
            fps (int): Frames per secont to run at.  Default: 30
            godmode (bool): Can the player die?  Default: False
            headless (bool): Skip creating the screen.
        """
        self.action_space = gym.spaces.Discrete(9*9)
        self.observation_space = gym.spaces.Box(0, 255, self.OUTPUT_SIZE)

        (top, left, bottom, right) = config.PLAY_AREA
        self.playArea = pygame.Rect(left, top, right - left, bottom - top)
        self.engine = Engine(config.SCREEN_SIZE, self.playArea, config.WAVES, level, fps, godmode)
        self._level = level
        self._lives = 3
        self._dead = False

    def reset(self):
        """
        Reset the game and get an initial observation

        returns:
            np.ndarray: The initial obs
        """
        print("Resetting")
        return self.get_state(self.engine.reset())

    def step(self,  action: int) -> Tuple[np.ndarray, int, bool, dict]:
        """
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
        (image, reward, score, lives, level, dead) = self.engine.update()

        self._lives = lives
        self._level = level
        self._dead = dead

        return self.get_state(image), reward, dead or level > 1, {
            'score': score,
            'level': level,
            'lives': lives
        }

    def get_state(self, image):
        """
        Convert the image into a 84 by 84 pixel image in a format for deep learning agents to easily consume.

        returns:
            np.ndarray: The 
        """
        image = crop(image, config.PLAY_AREA)
        image = np.transpose(image, (1, 0, 2))
        image = cv2.resize(image, self.OUTPUT_SIZE, interpolation=cv2.INTER_LINEAR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) / 255.
        return image

    def render(self):
        """ Tell the engine to render an image to the screen. """
        self.engine.render()

    @property
    def level(self):
        """ The current level """
        return self._level

    @property
    def lives(self):
        """ Current Lives Remaining """
        return self._lives

    @property
    def game_over(self):
        """ Is the game over? """
        return self._dead
