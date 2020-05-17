import pygame
import random

from .sprite_base import Base


class Family(Base):
    def __init__(self, sprites, engine, prefix):
        self.type = 'family'

        self.animations = {
            'left': [
                sprites[prefix + '1'],
                sprites[prefix + '2'],
                sprites[prefix + '1'],
                sprites[prefix + '3'],
            ],
            'right': [
                sprites[prefix + '4'],
                sprites[prefix + '5'],
                sprites[prefix + '4'],
                sprites[prefix + '6'],
            ],
            'down': [
                sprites[prefix + '7'],
                sprites[prefix + '8'],
                sprites[prefix + '7'],
                sprites[prefix + '9'],
            ],
            'up': [
                sprites[prefix + '10'],
                sprites[prefix + '11'],
                sprites[prefix + '10'],
                sprites[prefix + '12'],
            ]
        }

        self.scoreImage = {
            '1': sprites['1000'],
            '2': sprites['2000'],
            '3': sprites['3000'],
            '4': sprites['4000'],
            '5': sprites['5000'],
        }

        self.deathImage = sprites['familydeath']

        super().__init__(sprites, engine)
        self.alive = True

        self.moveSpeed = 4
        self.moveDelay = 5

        self.deathDelay = 15

        self.moveDirection = random.randrange(1, 8)
        self.random_location()

    def valid_move(self, direction):
        if not super().valid_move(direction):
            return False

        for sprite in self.engine.get_enemy_group():
            if sprite.type == 'electrode':
                if self.rect.colliderect(test):
                    return False

        return True

    def move(self):
        """ Family Members just choose a direction and go.  They change randomly or when they hit a wall. """
        self.update_animation()

        # If we move into a wall or quark, we need to choose a new direction
        direction = self.moveDirection
        validDirs = list(range(1, 8))
        while not self.valid_move(direction):
            if direction in validDirs:
                validDirs.remove(direction)
            if len(validDirs) == 0:
                direction = 0
                break
            else:
                direction = random.choice(validDirs)

        self.rect.topleft += self.get_vector(direction)
        self.moveDirection = direction

    def get_score(self):
        """ Happens in the engine """
        pass

    def collected(self):
        if self.alive:
            level = self.engine.family_collected()
            level = min(level, 5)
            self.image = self.scoreImage[str(level)]
            self.alive = False

    def die(self):
        if self.alive:
            self.image = self.deathImage
            self.alive = False

    def update(self):
        """
        Family members just keep walking continuously
        """
        if self.alive:
            if self.moveDelayRemaining <= 0:
                self.move()
                self.moveDelayRemaining = self.moveDelay
            else:
                self.moveDelayRemaining -= 1

            for sprite in pygame.sprite.spritecollide(self, self.engine.get_enemy_group(), False):
                if sprite.type == 'hulk':
                    self.die()
        else:
            self.deathDelay -= 1
            if self.deathDelay <= 0:
                self.kill()


class Mommy(Family):
    def __init__(self, sprites, engine):
        super().__init__(sprites, engine, 'mommy')
        self.type = 'mommy'


class Daddy(Family):
    def __init__(self, sprites, engine):
        super().__init__(sprites, engine, 'daddy')
        self.type = 'daddy'


class Mikey(Family):
    def __init__(self, sprites, engine):
        super().__init__(sprites, engine, 'mikey')
        self.type = 'mikey'
