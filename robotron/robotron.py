# -*- coding: utf-8 -*-
"""
Robotron 2084 Gymnasium Environment

A faithful recreation of Robotron 2084 as a Gymnasium environment for
reinforcement learning research.

Example:
    >>> from robotron import RobotronEnv
    >>> env = RobotronEnv()
    >>> obs, info = env.reset()
    >>> obs, reward, terminated, truncated, info = env.step(env.action_space.sample())

Or via gymnasium.make:
    >>> import gymnasium as gym
    >>> import robotron  # registers the env
    >>> env = gym.make('Robotron-v0', headless=True, always_move=True)
"""
from typing import Tuple, Optional
import numpy as np
import gymnasium as gym
import pygame

from .engine import Engine
from .utils import crop


class RobotronEnv(gym.Env):
    """
    Robotron 2084 Gymnasium Environment.

    Observation: RGB image of the play area (492x665x3 uint8)
    Action: Discrete — movement * directions + shooting
    Reward: score_delta / 100.0, death = -1.0
    """

    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 30}

    def __init__(self,
                 level: int = 1,
                 lives: int = 3,
                 fps: int = 0,
                 config_path: str = None,
                 godmode: bool = False,
                 always_move: bool = False,
                 render_mode: Optional[str] = None,
                 headless: bool = True,
                 max_episode_steps: Optional[int] = None,
                 seed: Optional[int] = None):
        """
        Args:
            level: Starting level (1-40).
            lives: Number of lives.
            fps: Frames per second (0 = unlimited, best for training).
            config_path: Path to custom config YAML.
            godmode: Invincibility for debugging.
            always_move: Drop no-op from action space (81 -> 64).
            render_mode: 'human' (pygame window) or 'rgb_array'.
            headless: Off-screen rendering. Automatically set to False
                      when render_mode='human'.
            max_episode_steps: Truncate episode after this many steps.
                               None = no limit (play until game over).
            seed: Deprecated — pass seed to reset() instead.
        """
        # render_mode='human' requires a display window
        if render_mode == 'human':
            headless = False

        self.engine = Engine(start_level=level, lives=lives, fps=fps, config_path=config_path,
                             godmode=godmode, headless=headless)
        width, height = self.engine.play_rect.size
        play_area = (height, width, 3)

        self.score = 0
        self._elapsed_steps = 0
        self._max_episode_steps = max_episode_steps

        # Gym Requirements
        self.action_mod = 1 if always_move else 0
        self.actions = 8 if always_move else 9
        self.action_space = gym.spaces.Discrete(self.actions * self.actions)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=play_area, dtype=np.uint8)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def get_board_size(self):
        """Returns (width, height) of the play area in pixels."""
        return self.engine.play_rect.size

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, dict]:
        """
        Reset the game and get an initial observation.

        Args:
            seed: Random seed for reproducibility.
            options: Additional reset options (unused).

        Returns:
            Tuple of (observation, info dict).
        """
        super().reset(seed=seed)

        self.engine.set_seed(self.np_random)

        self.score = 0
        self._elapsed_steps = 0
        obs, info = self.engine.reset()
        return self.get_state(obs), info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """
        Execute one game step.

        Args:
            action: Discrete action encoding movement and shooting.
                    action = movement_dir * num_directions + shoot_dir

        Returns:
            Tuple of (observation, reward, terminated, truncated, info).
        """
        if not 0 <= action < self.action_space.n:
            raise ValueError(f'Action {action} is invalid.')

        move = action // self.actions
        shoot = action % self.actions

        self.engine.handle_input(move + self.action_mod, shoot + self.action_mod)
        (image, score, lives, level, dead) = self.engine.update()

        reward = (self.engine.score - self.score) / 100.0
        self.score = self.engine.score

        if dead:
            reward = -1

        self._elapsed_steps += 1
        truncated = (self._max_episode_steps is not None
                     and self._elapsed_steps >= self._max_episode_steps)

        return self.get_state(image), reward, dead, truncated, {
            'score': score,
            'level': level,
            'lives': lives,
            'family': self.engine.family_remaining(),
            'data': self.engine.get_sprite_data(),
        }

    def get_state(self, image) -> np.ndarray:
        """Crop the full screen image to just the play area."""
        return crop(image, self.engine.play_area)

    def render(self):
        """
        Render the environment.

        Returns:
            ndarray if render_mode='rgb_array', None if 'human'.
        """
        if self.render_mode == 'rgb_array':
            return self.engine.get_image()
        elif self.render_mode == 'human':
            return None

    def close(self):
        """Clean up environment resources."""
        pygame.quit()
