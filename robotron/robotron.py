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
import gymnasium as gym
from typing import Optional

from .engine import Engine
from .utils import crop


class RobotronEnv(gym.Env):
    """
    The Robotron 2084 Environment.
    """

    FAMILY_REWARD = 10.0

    def __init__(self,
                 level: int = 1,
                 lives: int = 3,
                 fps: int = 0,
                 config_path: str = None,
                 godmode: bool = False,
                 always_move: bool = False,
                 render_mode: Optional[str] = None,
                 headless: bool = True,
                 seed: Optional[int] = None):
        """
        Setup the environment

        args:
            level (int): What level to start at.  Default: 1
            fps (int): Frames per secont to run at.  Default: 30
            godmode (bool): Are you a god? (Can't die.) Default: False
            always_move (bool): Always move/shoot.  Drops action space from 9x9 to 8x8  Default: False
            headless (bool): Skip creating the screen.
        """
        # TODO: Add game random number generator and use the seed
        self.engine = Engine(start_level=level, lives=lives, fps=fps, config_path=config_path,
                             godmode=godmode, headless=headless)
        width, height = self.engine.play_rect.size
        play_area = (height, width, 3)

        self.score = 0

        # Gym Requirements
        self.action_mod = 1 if always_move else 0
        self.actions = 8 if always_move else 9
        self.action_space = gym.spaces.Discrete(self.actions * self.actions)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=play_area, dtype=np.uint8)
        self.metadata = {'render.modes': ['human', 'rgb_array']}

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = 'rgb_array' if render_mode is None else render_mode

    def get_board_size(self):
        """
        Get the size of the board

        returns:
            (int, int): The width and height of the board
        """

        return self.engine.play_rect.size

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> np.ndarray:
        """
        Reset the game and get an initial observation

        returns:
            np.ndarray: The initial obs
        """
        super().reset(seed=seed)
        self.score = 0
        obs, info = self.engine.reset()
        return self.get_state(obs), info

    def step(self,  action: int) -> Tuple[np.ndarray, int, bool, dict]:
        r"""
        Play one frame of the game.  We return the obs, reward, done, and
        any additional info.  Follows the openai gym observations structure.
        https://gym.openai.com/docs/#observations

        args:
            action (int): The inputs to the game. This consists of two ints between 0-8
            following the cardinal points of the joystick.

                8   1   2
                  \ | /
                7 - 0 - 3
                  / | \
                6   5   4

            If we have always_move set to True, we drop the Noop action. (Basically add 1 to each action)

            Final equation should be: 
            ```python
            actions = 8 if always_move else 9
            action = left * actions + right
            ```

        returns:
            (np.ndarray, float, bool, dict): the obs, reward, done, and info

        raises:
            ValueError: Raised if input is invalid.
        """

        if not 0 <= action <= self.action_space.n:
            raise ValueError(f'Action {action} is invalid.')

        move = action // self.actions
        shoot = action % self.actions

        self.engine.handle_input(move + self.action_mod, shoot + self.action_mod)
        (image, score, lives, level, dead) = self.engine.update()

        reward = (self.engine.score - self.score) / 100.0
        self.score = self.engine.score

        if dead:
            reward = -1

        truncated = False  # We don't have a time limit.  You play until you die.

        return self.get_state(image), reward, dead, truncated, {
            'score': score,
            'level': level,
            'lives': lives,
            'family': self.engine.family_remaining(),
            'data': self.engine.get_sprite_data(),
        }

    def get_state(self, image) -> np.ndarray:
        """
        Return only the play area of the image.

        returns:
            np.ndarray: The game image for the current step
        """
        image = crop(image, self.engine.play_area)
        return image

    def render(self, mode='human'):
        """ TODO:  Render the game on the screen while playing.  Currently automatically does this via pygame. """
        image = self.engine.get_image()
        if mode == 'human':
            return image
        else:
            return self.get_state(image)
