# -*- coding: utf-8 -*-
"""The Robotron Game Engine"""
import math
import os
from enum import Enum, auto
from typing import List, Tuple, Dict, Optional

import numpy as np
import pygame

from .config import Config
from .graphics import load_graphics
from .entities import Player, Mommy, Daddy, Mikey, Grunt, Electrode, Hulk, Sphereoid, Quark, Brain


class GameState(Enum):
    """Engine state machine states."""
    WARPING_IN = auto()
    PLAYING = auto()
    DYING = auto()
    LEVEL_COMPLETE = auto()


class Engine:
    """
    Robotron game engine.

    Todo:
        Remove the RL stuff from this class.  Doesn't really belong here.  Only here because I'm lazy.
        Better approach is to return all the information needed and let the Env wrapper figure out the
        rewards.
    """

    def __init__(self,
                 start_level: int = 1,
                 lives: int = 3,
                 fps: int = 0,
                 config_path: str = None,
                 godmode: bool = False,
                 headless: bool = False):
        self.godmode = godmode
        self.start_level = start_level - 1
        self.level = self.start_level
        self.start_lives = lives
        self.lives = lives
        self.fps = fps
        self.headless = headless

        self.score = 0
        self.extra_lives = 0
        self.done = False
        self.frame = 0
        self.np_random = None

        self.config = Config(config_path)

        # Set headless mode BEFORE pygame.init()
        if headless:
            print("Running in headless mode (off-screen rendering).")
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"  # Disable audio to prevent ALSA warnings

        pygame.init()

        screen_size = self.config.get('screen_size')

        if headless:
            # Create a minimal display for .convert() then use off-screen surface
            pygame.display.set_mode((1, 1))  # Minimal display
            self.screen = pygame.Surface(screen_size)
        else:
            # Create a display window
            self.screen = pygame.display.set_mode(screen_size)
            pygame.display.set_caption('Robotron 2084')

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.graphics = load_graphics()

        self.play_area = self.config.get('play_area')
        (top, left, bottom, right) = self.play_area
        self.play_rect = pygame.Rect(left, top, right - left, bottom - top)

        self.family_group = pygame.sprite.Group()  # Enemies and their bullets.
        self.enemy_group = pygame.sprite.Group()  # Enemies and their bullets.
        self.to_kill_group = pygame.sprite.Group()  # Enemies that need to die to advance the level.
        self.all_group = pygame.sprite.Group()  # All sprites on screen.
        self.waves = self.config.get('waves')
        self.to_kill_group_types = ['Grunt', 'Sphereoid', 'Enforcer', 'Brain', 'Quark', 'Tank', 'Prog']

        self.extra_life_score = self.config.get('extra_life_score')
        self.player = None
        self.player_box = None
        self.family_collected = 0

        # State machine for game phases
        self.state = GameState.PLAYING
        self.state_timer = 0
        self.warp_in_duration = self.config.get('warp_in_duration', 30)
        self.death_duration = self.config.get('death_duration', 30)
        self.level_complete_duration = self.config.get('level_complete_duration', 20)
        self._warp_in_sprites = []
        self._game_over_pending = False

        # Visual effects
        self.effects_enabled = self.config.get('effects_enabled', True)
        # Arcade-style border color palette (cycles continuously)
        self._border_colors = [
            (238, 5, 8),     # Red (original)
            (255, 100, 0),   # Orange
            (255, 255, 0),   # Yellow
            (0, 255, 0),     # Green
            (0, 200, 255),   # Cyan
            (100, 100, 255), # Blue
            (200, 0, 255),   # Purple
            (255, 0, 200),   # Pink
        ]

        self._initialize_level()

    def set_seed(self, np_random: np.random.Generator) -> None:
        """
        Set the numpy random number generator for the engine.

        Args:
            np_random: The numpy random generator from the environment
        """
        self.np_random = np_random

    def handle_input(self, move: int, shoot: int) -> None:
        """
        Handle Player Input

        Args:
            move: Movement direction (0-8)
            shoot: Shooting direction (0-8)
        """
        if not self.done and self.state == GameState.PLAYING:
            self.player.move(move)
            self.player.shoot(shoot)

    def set_level(self, level: int) -> None:
        """
        Change the level

        Args:
            level: The level to select (1-indexed)
        """
        self.level = level - 1
        self._initialize_level()

    # State Management
    def _initialize_level(self):
        """
        Setup a new level.  Removes existing sprites, setups up new sprites.  Zero level values.
        Starts in WARPING_IN state so enemies materialize before gameplay begins.
        """
        for sprite in self.all_group:
            sprite.kill()

        self.player = Player(self)
        self._add_sprite(self.player)

        self.player_box = None
        self.family_collected = 0

        # Load all family/enemies for the level.  Mikey should be first to facilitate the 'Mikey bug'
        # Calculate which wave to use based on level and repeat behavior
        wave_level = self._calculate_wave_level(self.level)
        level_data = self.waves[wave_level]
        (grunts, electrodes, hulks, brains, sphereoids, quarks, mommies, daddies, mikeys) = level_data
        _ = [self._add_family(Mikey(self)) for _ in range(mikeys)]
        _ = [self._add_family(Mommy(self)) for _ in range(mommies)]
        _ = [self._add_family(Daddy(self)) for _ in range(daddies)]
        _ = [self._add_enemy(Grunt(self)) for _ in range(grunts)]
        _ = [self._add_enemy(Electrode(self)) for _ in range(electrodes)]
        _ = [self._add_enemy(Hulk(self)) for _ in range(hulks)]
        _ = [self._add_enemy(Sphereoid(self)) for _ in range(sphereoids)]
        _ = [self._add_enemy(Quark(self)) for _ in range(quarks)]
        _ = [self._add_enemy(Brain(self)) for _ in range(brains)]

        # Store original sprite images for warp-in effect
        if self.warp_in_duration > 0:
            self._warp_in_sprites = []
            for sprite in self.all_group:
                if sprite != self.player:
                    self._warp_in_sprites.append((sprite, sprite.image.copy()))
            self.state = GameState.WARPING_IN
            self.state_timer = self.warp_in_duration
        else:
            self.state = GameState.PLAYING

    def _set_family_collected(self) -> int:
        """
        Called when the player collects a human.
        You get 1000 for the first human rescued. Then it will progress at 2000, 3000,
        4000, then 5000 for every human rescued after that.  This will last the entire
        wave or until you get killed.  If you get killed or go to a new wave, then the
        progression starts at 1000 again.

        Returns:
            The number of humans collected this level.
        """
        self.family_collected += 1
        self.score += min(self.family_collected * 1000, 5000)
        return self.family_collected

    def _calculate_wave_level(self, level: int) -> int:
        """
        Calculate which wave configuration to use for a given level.
        
        Supports the original Robotron behavior:
        - Levels 0-39: Use waves 0-39
        - Level 40+: Repeat starting from wave 20 (so level 40 = wave 20, 41 = wave 21, etc.)
        
        Also supports custom repeat behavior via 'repeat_at' config option.
        If no repeat_at is specified and we don't have exactly 40 waves,
        cycles through all available waves.
        
        Args:
            level: The current level (0-indexed)
            
        Returns:
            The wave index to use (0-indexed)
        """
        num_waves = len(self.waves)
        repeat_at = self.config.get('repeat_at', None)
        
        # If we have a specific repeat_at configuration
        if repeat_at is not None:
            if level < num_waves:
                return level
            else:
                # After exhausting all waves, repeat starting from repeat_at
                cycle_length = num_waves - repeat_at
                return repeat_at + ((level - repeat_at) % cycle_length)
        
        # Original Robotron behavior: 40 waves, then repeat from wave 20
        elif num_waves == 40:
            if level < 40:
                return level
            else:
                # After level 39 (wave 39), repeat starting from wave 20 (level 21)
                # Level 40 -> wave 20, Level 41 -> wave 21, etc.
                return 20 + ((level - 40) % 20)
        
        # Default behavior: cycle through all available waves
        else:
            return level % num_waves

    def _get_play_area_distance(self) -> float:
        """
        Get the distance from the top left to the bottom right of the play area.  This is the
        maximum distance from the player an enemy can be.

        Returns:
            The max distance two sprites can be in the play area.
        """
        w, h = self.play_rect.size
        return math.hypot(w, h)

    # Sprite Management
    def _get_family_group(self) -> pygame.sprite.Group:
        """
        Get the group of all family sprites.

        Returns:
            pygame.sprite.Group: The group of all the family sprites.
        """
        return self.family_group

    def _get_enemy_group(self) -> pygame.sprite.Group:
        """
        Returns all sprites listed as an enemy.

        Returns:
            pygame.sprite.Group: The group of enemy sprites.
        """
        return self.enemy_group

    def _get_all_group(self) -> pygame.sprite.Group:
        """
        Get all sprites on screen.

        Returns:
            pygame.sprite.Group: A group of all sprites.
        """
        return self.all_group

    def _get_sprite(self, sprite_name: str) -> pygame.Surface:
        """
        Return the sprite graphics by name.

        Args:
            sprite_name (str): The name of the sprite we want.

        Returns:
            pygame.Surface: The image of the sprite.
        """
        return self.graphics[sprite_name]

    def _get_sprites(self, sprite_names: List[str]) -> List[pygame.Surface]:
        """
        Get the images for all sprites in a list.

        Args:
            sprite_names (List[str]): A list of image names.

        Returns:
            List[pygame.Surface]: The list of images.
        """
        return [self.graphics[name] for name in sprite_names]

    def _get_player_box(self) -> pygame.Rect:
        """
        Safe area around player to not place enemies on load.

        Returns:
            The rect around the player to ignore when loading enemies.
        """
        if self.player_box is None:
            (x, y) = self.player.rect.center
            (w, h) = (self.play_rect.width // 3, self.play_rect.height // 3)
            self.player_box = pygame.Rect(x - w // 2, y - h // 2, w, h)

        return self.player_box

    def _add_background(self) -> None:
        """Set the background color and draw the play area border with optional color cycling."""
        self.screen.fill((0, 0, 0))

        if self.effects_enabled:
            # Border cycles through colors; faster during level complete/warp-in
            if self.state in (GameState.LEVEL_COMPLETE, GameState.WARPING_IN):
                color_idx = (self.frame * 3) % len(self._border_colors)
            else:
                color_idx = (self.frame // 4) % len(self._border_colors)
            border_color = self._border_colors[color_idx]
        else:
            border_color = (238, 5, 8)

        pygame.draw.rect(self.screen, border_color, self.play_rect.inflate(15, 15), 5)

    def _add_info(self) -> None:
        """Add the text info for human consumption. Does not replicate the original game."""
        text = self.font.render(
            f'Score: {self.score} Level: {self.level + 1} Lives: {self.lives} {"GAME OVER" if self.done else ""}',
            True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(text, (self.play_rect.x, self.play_rect.y - 40))

    def _add_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """
        Add a sprite to the screen. Used for sprites that do not interact with the player.

        Args:
            sprite: The sprite to add.
        """
        self.all_group.add(sprite)

    def _add_family(self, family: pygame.sprite.Sprite) -> None:
        """
        Add a family member. These sprites are collected by the player and targeted by some enemies.

        Args:
            family: The family member to add.
        """
        self.family_group.add(family)
        self.all_group.add(family)

    def _add_enemy(self, enemy: pygame.sprite.Sprite) -> None:
        """
        Add an enemy sprite. These sprites are harmful to the player.

        Args:
            enemy: The enemy to add.
        """
        self.enemy_group.add(enemy)
        self.all_group.add(enemy)

        if enemy.__class__.__name__ in self.to_kill_group_types:
            self.to_kill_group.add(enemy)

    # Lifecycle Management
    def update(self) -> Tuple[np.ndarray, int, int, int, bool]:
        """
        The main update loop. Manages game state transitions and triggers world updates.

        Returns:
            Tuple of (image, score, lives, level, done)
        """
        pygame.event.pump()
        self.clock.tick(self.fps)
        self.frame += 1

        # Extra life check
        if self.extra_life_score > 0:
            if self.score // self.extra_life_score > self.extra_lives:
                self.lives += 1
                self.extra_lives += 1

        if not self.done:
            if self.state == GameState.WARPING_IN:
                self._update_warp_in()
            elif self.state == GameState.PLAYING:
                self._update_playing()
            elif self.state == GameState.DYING:
                self._update_dying()
            elif self.state == GameState.LEVEL_COMPLETE:
                self._update_level_complete()

        # Always draw (to off-screen surface in headless mode)
        self.draw()

        image = self.get_image()

        return (image, self.score, self.lives, self.level, self.done)

    def _update_warp_in(self):
        """
        Warp-in phase: enemies materialize from small dots to full size.
        In the arcade, enemies appear as colored pixels that expand to their full sprites.
        """
        self.state_timer -= 1
        progress = 1.0 - (self.state_timer / self.warp_in_duration)

        for sprite, original_image in self._warp_in_sprites:
            if sprite not in self.all_group:
                continue
            orig_w, orig_h = original_image.get_size()
            # Scale from a tiny dot up to full size
            w = max(2, int(orig_w * progress))
            h = max(2, int(orig_h * progress))
            center = sprite.rect.center
            scaled = pygame.transform.scale(original_image, (w, h))

            # Color tint effect during warp-in: flash through colors
            if self.effects_enabled and progress < 0.85:
                tint_color = self._border_colors[(self.frame * 2) % len(self._border_colors)]
                tint_surface = pygame.Surface((w, h), pygame.SRCALPHA)
                tint_surface.fill((*tint_color, 120))
                scaled = scaled.copy()
                scaled.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            sprite.image = scaled
            sprite.rect = sprite.image.get_rect(center=center)

        if self.state_timer <= 0:
            # Restore original images
            for sprite, original_image in self._warp_in_sprites:
                if sprite not in self.all_group:
                    continue
                center = sprite.rect.center
                sprite.image = original_image
                sprite.rect = sprite.image.get_rect(center=center)
            self._warp_in_sprites = []
            self.state = GameState.PLAYING

    def _update_playing(self):
        """Normal gameplay: update sprites, check collisions, check level clear."""
        self.all_group.update()

        # Check to see if we hit an enemy
        if not self.godmode and pygame.sprite.spritecollide(self.player, self.enemy_group, False):
            self.family_collected = 0
            if self.lives > 0:
                self.lives -= 1
                self._start_death_sequence()
            else:
                self._start_death_sequence(game_over=True)

        elif not self.to_kill_group:
            if self.level_complete_duration > 0:
                self.state = GameState.LEVEL_COMPLETE
                self.state_timer = self.level_complete_duration
            else:
                self.level += 1
                self._initialize_level()

    def _start_death_sequence(self, game_over=False):
        """Begin the player death pause. Sprites freeze, then reset."""
        self._game_over_pending = game_over
        if self.death_duration > 0:
            self.state = GameState.DYING
            self.state_timer = self.death_duration
            # Hide the player sprite during death pause
            self.player.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        else:
            self._finish_death_sequence()

    def _update_dying(self):
        """Death pause: all sprites frozen, just count down."""
        self.state_timer -= 1
        if self.state_timer <= 0:
            self._finish_death_sequence()

    def _finish_death_sequence(self):
        """Complete the death: either game over or reset sprites for respawn."""
        if self._game_over_pending:
            self.done = True
        else:
            for sprite in self.all_group:
                sprite.reset()
            self.state = GameState.PLAYING

    def _update_level_complete(self):
        """Brief pause after clearing all enemies before advancing."""
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.level += 1
            self._initialize_level()

    def draw(self) -> None:
        """Paint the window or off-screen surface."""
        self._add_background()
        self._add_info()
        self.all_group.draw(self.screen)

        if self.effects_enabled:
            # Level complete: rapid flash overlay
            if self.state == GameState.LEVEL_COMPLETE:
                if self.frame % 4 < 2:
                    flash = pygame.Surface(self.play_rect.size, pygame.SRCALPHA)
                    flash.fill((255, 255, 255, 40))
                    self.screen.blit(flash, self.play_rect.topleft)

        # Only update display if not in headless mode
        if not self.headless:
            pygame.display.update()

    def family_remaining(self) -> int:
        """
        Return the number of family members remaining.

        Returns:
            The number of family members remaining.
        """
        return len(self.family_group)

    def get_sprite_data(self) -> List[Tuple[int, int, str]]:
        """
        Get the data for all meaningful sprites. Includes players, bullets, and enemies.
        We skip floaters since those are just trails or points and can't be interacted with.

        Returns:
            A list of tuples of (x, y, sprite_name) relative to play area.
        """
        (top, left, _, _) = self.play_area

        # Use list comprehension for better performance
        return [
            (sprite.rect.x - left, sprite.rect.y - top, sprite.__class__.__name__)
            for sprite in self.all_group
            if sprite.__class__.__name__ != 'Floater'
        ]

    def reset(self) -> Tuple[np.ndarray, Dict]:
        """
        Reset the game

        Returns:
            Tuple of (initial image, info dict)
        """
        self.frame = 0
        self.level = self.start_level
        self.score = 0
        self.lives = self.start_lives
        self.extra_lives = 0
        self.done = False
        self._game_over_pending = False

        self._initialize_level()

        # Draw the initial state
        self.draw()

        return self.get_image(), {
            'score': self.score,
            'level': self.level,
            'lives': self.lives,
            'family': self.family_remaining(),
            'data': self.get_sprite_data(),
        }

    def get_image(self) -> np.ndarray:
        """
        Return the latest image.

        Returns:
            An image array.
        """
        # In headless mode, use the off-screen surface directly
        # Otherwise use the display surface
        surface = self.screen if self.headless else pygame.display.get_surface()
        return pygame.surfarray.array3d(surface).swapaxes(0, 1)
