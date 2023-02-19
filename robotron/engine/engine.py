# -*- coding: utf-8 -*-
"""The Robotron Game Engine"""
import math
import os
from typing import List, Tuple

import pygame

from .config import Config
from .graphics import load_graphics
from .entities import Player, Mommy, Daddy, Mikey, Grunt, Electrode, Hulk, Sphereoid, Quark, Brain


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

        self.score = 0
        self.extra_lives = 0
        self.done = False
        self.frame = 0

        self.config = Config(config_path)

        pygame.init()
        pygame.display.set_caption('Robotron 2084')

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

        screen_size = self.config.get('screen_size')
        if headless:
            print("Using dummy video driver.")
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            # screen_size = (1, 1)

        self.screen = pygame.display.set_mode(screen_size)
        self.graphics = load_graphics()

        self.play_area = self.config.get('play_area')
        (top, left, bottom, right) = self.play_area
        self.play_rect = pygame.Rect(left, top, right - left, bottom - top)

        self.family_group = pygame.sprite.Group()  # Enemies and their bullets.
        self.enemy_group = pygame.sprite.Group()  # Enemies and their bullets.
        self.to_kill_group = pygame.sprite.Group()  # Enemies that need to die to advance the level.
        self.all_group = pygame.sprite.Group()  # All sprites on screen.
        self.waves = self.config.get('waves')
        self.to_kill_group_types = ['Grunt', 'Sphereoid', 'Enforcer', 'Brain', 'Quark', 'Tank']
        self.enemies = ['grunt', 'electrode', ]

        self.extra_life_score = self.config.get('extra_life_score')
        self.player = None
        self.player_box = None
        self.family_collected = 0

        self._initialize_level()

    def handle_input(self, move, shoot):
        """ Handle Player Input """
        if not self.done:
            self.player.move(move)
            self.player.shoot(shoot)

    def set_level(self, level):
        """
        Change the level

        Args:
            level (int): The level to select.
        """
        self.level = level - 1
        self._initialize_level()

    # State Management
    def _initialize_level(self):
        """
        Setup a new level.  Removes existing sprites, setups up new sprites.  Zero level values.
        """
        for sprite in self.all_group:
            sprite.kill()

        self.player = Player(self)
        self._add_sprite(self.player)

        self.family_collected = 0

        # Load all family/enemies for the level.  Mikey should be first to facilitate the 'Mikey bug'
        wave_level = self.level if self.level < 20 else 20 + self.level % 20
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

    def _set_family_collected(self):
        """
        Called when the player collects a human.
        You get 1000 for the first human rescued. Then it will progress at 2000, 3000,
        4000, then 5000 for every human rescued after that.  This will last the entire
        wave or until you get killed.  If you get killed or go to a new wave, then the
        progression starts at 1000 again.

        Returns:
            int: The number of humans collected this level.
        """
        self.family_collected += 1
        self.score += min(self.family_collected * 1000, 5000)
        return self.family_collected

    def _get_play_area_distance(self):
        """
        Get the distance from the top left to the bottom right of the play area.  This is the
        maximum distance from the player an enemy can be.

        Returns:
            float: The max distance two sprites can be in the play area.
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

    def _get_player_box(self):
        """
        Safe area around player to not place enemies on load.

        Returns:
            pygame.Rect: The rect around the player to ignore when loading enemies.
        """
        if self.player_box is None:
            (x, y) = self.player.rect.center
            (w, h) = (self.play_rect.width // 3, self.play_rect.height // 3)
            self.player_box = pygame.Rect(x - w // 2, y - h // 2, w, h)

        return self.player_box

    def _add_background(self):
        """ Set the background color and draw the play area box """
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, [238, 5, 8], self.play_rect.inflate(15, 15), 5)

    def _add_info(self):
        """ Add the text info for human consumption.  Does not replicate the original game. """
        text = self.font.render(
            f'Score: {self.score} Level: {self.level + 1} Lives: {self.lives} {"GAME OVER" if self.done else ""}',
            True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(text, (self.play_rect.x, self.play_rect.y - 40))

    def _add_sprite(self, sprite: pygame.sprite):
        """
        Add a sprite to the screen.  Used for sprites that do not interact with the player.

        Args:
            sprite (pygame.sprite): The sprite to add.
        """
        self.all_group.add(sprite)

    def _add_family(self, family: pygame.sprite):
        """
        Add a family member.  These sprites are collected by the player and targeted by some enemies.

        Args:
            family (pygame.sprite): The family member to add.
        """
        self.family_group.add(family)
        self.all_group.add(family)

    def _add_enemy(self, enemy: pygame.sprite):
        """
        Add an enemy sprite.  These sprites are harmful to the player.

        Args:
            enemy (pygame.sprite): The enemy to add.
        """
        self.enemy_group.add(enemy)
        self.all_group.add(enemy)

        if enemy.__class__.__name__ in self.to_kill_group_types:
            self.to_kill_group.add(enemy)

    # Lifecycle Management
    def update(self):
        """
        The allmighty update loops. Triggers the world update.

        """
        pygame.event.pump()
        self.clock.tick(self.fps)
        self.frame += 1

        # You start the game with 3 men and receive and additional man for every 25,000 points you get.
        if self.extra_life_score > 0:
            if self.score // self.extra_life_score > self.extra_lives:
                self.lives += 1
                self.extra_lives += 1

        if not self.done:
            self.all_group.update()

            # Check to see if we hit an enemy
            if not self.godmode and pygame.sprite.spritecollide(self.player, self.enemy_group, False):
                self.family_collected = 0
                if self.lives > 0:
                    self.lives -= 1
                    for sprite in self.all_group:
                        sprite.reset()
                else:
                    self.done = True

            if not self.to_kill_group:
                self.level += 1
                self._initialize_level()

        self.draw()
        image = self.get_image()

        return (image, self.score, self.lives, self.level, self.done)

    def draw(self):
        """ Paint the window. """
        self._add_background()
        self._add_info()
        self.all_group.draw(self.screen)
        pygame.display.update()

    def family_remaining(self):
        """
        Return the number of family members remaining.

        Returns:
            int: The number of family members remaining.
        """
        return len(self.family_group)

    def get_sprite_data(self) -> List[Tuple[int, int, str]]:
        """
        Get the data for all meaningful sprites.  Includes players, bullets, and enemies.
        We skip floaters since those are just trails or points and can't be interacted with.

        Returns:
            List[Tuple[int, int, str]]: A list of tuples of (x, y, sprite_name).
        """
        (top, left, _, _) = self.play_area

        data = []
        for enemy in self.all_group:
            if enemy.__class__.__name__ != 'Floater':
                data.append((enemy.rect.x - left, enemy.rect.y - top, enemy.__class__.__name__))

        return data

    def reset(self):
        """
        Reset the game

        Returns:
            List: Returns the initial image.
        """
        self.frame = 0
        self.level = self.start_level
        self.score = 0
        self.lives = self.start_lives
        self.extra_lives = 0
        self.done = False

        self._initialize_level()

        return self.get_image()

    @staticmethod
    def get_image() -> List:
        """
        Return the latest image.

        Returns:
            List: An image array.
        """
        return pygame.surfarray.array3d(pygame.display.get_surface()).swapaxes(0, 1)
