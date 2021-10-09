# -*- coding: utf-8 -*-
import math
import pygame
import os

from typing import Tuple, List

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
                 screen_size: Tuple[int, int],
                 playRect: pygame.Rect,
                 waveInfo: Tuple[Tuple],
                 startLevel: int = 1,
                 fps: int = 0,
                 godmode: bool = False,
                 headless: bool = False):
        self.playRect = playRect
        self.playRectDistance = None
        self.waveInfo = waveInfo
        self.godmode = godmode
        self.startLevel = startLevel - 1
        self.level = self.startLevel
        self.fps = fps
        self.lives = 3
        self.score = 0
        self.extraLives = 0
        self.done = False
        self.frame = 0

        self.default_reward = -0.1
        self.reward = self.default_reward

        pygame.init()
        pygame.display.set_caption('Robotron 2084')

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

        if headless:
            print("Using dummy video driver.")
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            screen_size = (1, 1)

        self.screen = pygame.display.set_mode(screen_size)
        self.graphics = load_graphics()

        self.familyGroup = pygame.sprite.Group()  # Enemies and their bullets.
        self.enemyGroup = pygame.sprite.Group()  # Enemies and their bullets.
        self.toKillGroup = pygame.sprite.Group()  # Enemies that need to die to advance the level.
        self.allGroup = pygame.sprite.Group()  # All sprites on screen.
        self.toKillGroupTypes = ['Grunt', 'Sphereoid', 'Enforcer', 'Brain', 'Quark', 'Tank']
        self.enemies = ['grunt', 'electrode', ]

        self.player = None
        self.playerBox = None
        self.familyCollected = 0

        self.initialize_level()

    def handle_input(self, move, shoot):
        """ Handle Player Input """
        if not self.done:
            self.player.move(move)
            self.player.shoot(shoot)

    # State Management

    def initialize_level(self):
        for sprite in self.allGroup:
            sprite.kill()

        self.player = Player(self)
        self.add_sprite(self.player)

        self.familyCollected = 0

        # Load all family/enemies for the level.  Mikey should be first to facilitate the 'Mikey bug'
        waveLevel = self.level if self.level < 20 else 20 + self.level % 20
        levelData = self.waveInfo[waveLevel]
        print("Level:", waveLevel)

        (grunts, electrodes, hulks, brains, sphereoids, quarks, mommies, daddies, mikeys) = levelData
        [self.add_family(Mikey(self)) for _ in range(mikeys)]
        [self.add_family(Mommy(self)) for _ in range(mommies)]
        [self.add_family(Daddy(self)) for _ in range(daddies)]
        [self.add_enemy(Grunt(self)) for _ in range(grunts)]
        [self.add_enemy(Electrode(self)) for _ in range(electrodes)]
        [self.add_enemy(Hulk(self)) for _ in range(hulks)]
        [self.add_enemy(Sphereoid(self)) for _ in range(sphereoids)]
        [self.add_enemy(Quark(self)) for _ in range(quarks)]
        [self.add_enemy(Brain(self)) for _ in range(brains)]

    def add_score(self, score):
        self.score += score
        self.reward = min(1.0, self.reward + 0.3)

    def get_score(self):
        return self.score

    def family_collected(self):
        """
        You get 1000 for the first human rescued. Then it will progress at 2000, 3000,
        4000, then 5000 for every human rescued after that.  This will last the entire
        wave or until you get killed.  If you get killed or go to a new wave, then the
        progression starts at 1000 again.
        """
        self.familyCollected += 1
        self.score += min(self.familyCollected * 1000, 5000)
        self.reward = 1.0
        return self.familyCollected

    def set_level(self, level):
        self.level = level - 1
        self.initialize_level()

    def get_level(self):
        return self.level

    def get_play_area(self):
        return self.playRect

    def get_play_area_distance(self):
        if not self.playRectDistance:
            w, h = self.playRect.size
            self.playRectDistance = math.hypot(w, h)
        return self.playRectDistance

    def get_player(self):
        return self.player

    def get_family_group(self):
        return self.familyGroup

    def get_enemy_group(self):
        return self.enemyGroup

    def get_all_group(self):
        return self.allGroup

    # Sprite Management
    def get_sprite(self, sprite_name: str):
        return self.graphics[sprite_name]

    def get_sprites(self, sprite_names: List[str]):
        return [self.graphics[name] for name in sprite_names]

    def get_player_box(self):
        """ Safe area around player to not place enemies on load. """
        if self.playerBox is None:
            (x, y) = self.player.rect.center
            (w, h) = (self.playRect.width // 3, self.playRect.height // 3)
            self.playerBox = pygame.Rect(x - w // 2, y - h // 2, w, h)

        return self.playerBox

    def add_background(self):
        """ Set the background color and draw the play area box """
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, [238, 5, 8], self.playRect.inflate(15, 15), 5)

    def add_info(self):
        """ Add the text info for human consumption.  Does not replicate the original game. """
        text = self.font.render(
            f'Score: {self.score} Level: {self.level + 1} Lives: {self.lives} {"GAME OVER" if self.done else ""}',
            True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(text, (self.playRect.x, self.playRect.y - 40))

    def add_sprite(self, sprite):
        self.allGroup.add(sprite)

    def add_family(self, family):
        self.familyGroup.add(family)
        self.allGroup.add(family)

    def add_enemy(self, enemy):
        self.enemyGroup.add(enemy)
        self.allGroup.add(enemy)

        if enemy.__class__.__name__ in self.toKillGroupTypes:
            self.toKillGroup.add(enemy)

    # Lifecycle Management

    def update(self):
        """
        The allmighty update loops.  Runs once per frame to update the world.

        """
        pygame.event.pump()
        self.clock.tick(self.fps)
        self.frame += 1

        # You start the game with 3 men and receive and additional man for every 25,000 points you get.
        if self.score // 25000 > self.extraLives:
            self.lives += 1
            self.extraLives += 1

        if not self.done:
            self.allGroup.update()

            # Check to see if we hit an enemy
            if not self.godmode and pygame.sprite.spritecollide(self.player, self.enemyGroup, False):
                self.familyCollected = 0
                if self.lives > 0:
                    self.lives -= 1
                    for sprite in self.allGroup:
                        sprite.zero()
                        sprite.reset()
                else:
                    self.done = True

            if not self.toKillGroup:
                self.level += 1
                self.initialize_level()

        reward = self.reward
        self.reward = self.default_reward

        self.draw()
        image = self.get_image()

        return (image, reward, self.score, self.lives, self.level, self.done)

    def draw(self):
        self.add_background()
        self.add_info()
        self.allGroup.draw(self.screen)
        pygame.display.update()

    def reset(self):
        self.frame = 0
        self.level = self.startLevel
        self.score = 0
        self.lives = 3
        self.extraLives = 0
        self.done = False

        self.initialize_level()

        return self.get_image()

    def get_image(self):
        """
        Return the latest image.
        """
        imgdata = pygame.surfarray.array3d(pygame.display.get_surface())
        imgdata = imgdata.swapaxes(0, 1)
        return imgdata

    def render(self):
        pass
