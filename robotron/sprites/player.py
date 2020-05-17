import pygame


class Bullet(pygame.sprite.Sprite):
    UP = 1
    UP_RIGHT = 2
    RIGHT = 3
    DOWN_RIGHT = 4
    DOWN = 5
    DOWN_LEFT = 6
    LEFT = 7
    UP_LEFT = 8

    def __init__(self, engine, x, y, direction, playRect):
        super().__init__()
        self.type = 'playerbullet'
        self.engine = engine

        width = height = 16
        weight = 2

        self.moveSpeed = 15
        self.playRect = playRect

        self.direction = direction
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface([width, height]).convert()

        if direction in [self.UP, self.DOWN]:
            pygame.draw.line(self.image, [255, 255, 255], (width // 2, 0), (width // 2, height), weight)
        elif direction in [self.RIGHT, self.LEFT]:
            pygame.draw.line(self.image, [255, 255, 255], (0, height // 2), (width, height // 2), weight)
        elif direction in [self.UP_RIGHT, self.DOWN_LEFT]:
            pygame.draw.line(self.image, [255, 255, 255], (width, 0), (0, height), weight)
        else:
            pygame.draw.line(self.image, [255, 255, 255], (0, 0), (width, height), weight)

    def update(self):
        if self.direction in [self.UP, self.UP_LEFT, self.UP_RIGHT]:
            self.rect.y -= self.moveSpeed
        if self.direction in [self.DOWN, self.DOWN_LEFT, self.DOWN_RIGHT]:
            self.rect.y += self.moveSpeed
        if self.direction in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
            self.rect.x -= self.moveSpeed
        if self.direction in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
            self.rect.x += self.moveSpeed

        killed = pygame.sprite.spritecollide(self, self.engine.get_enemy_group(), False)
        if killed:
            sprite = killed[0]
            self.engine.add_score(sprite.get_score())
            sprite.die()
            self.kill()

        if not self.playRect.contains(self.rect):
            self.kill()

    def zero(self):
        self.kill()

    def reset(self):
        self.kill()


class Player(pygame.sprite.Sprite):
    UP = 1
    UP_RIGHT = 2
    RIGHT = 3
    DOWN_RIGHT = 4
    DOWN = 5
    DOWN_LEFT = 6
    LEFT = 7
    UP_LEFT = 8

    def __init__(self, sprites, engine):
        super().__init__()

        self.type = 'player'

        self.playRect = engine.get_play_area()
        self.engine = engine
        self.moveSpeed = 5
        self.shootDelay = 5
        self.shootDelayRemaining = 0
        self.animationStep = 0
        self.animationDirection = 'down'

        self.animations = {
            'left': [
                sprites['player1'],
                sprites['player2'],
                sprites['player1'],
                sprites['player3'],
            ],
            'right': [
                sprites['player4'],
                sprites['player5'],
                sprites['player4'],
                sprites['player6'],
            ],
            'down': [
                sprites['player7'],
                sprites['player8'],
                sprites['player7'],
                sprites['player9'],
            ],
            'up': [
                sprites['player10'],
                sprites['player11'],
                sprites['player10'],
                sprites['player12'],
            ]
        }
        self.reset()

    def move(self, move):
        if move:
            dir = 'down'
            if move in [self.UP, self.UP_LEFT, self.UP_RIGHT]:
                self.rect.y -= self.moveSpeed
                dir = 'up'
            if move in [self.DOWN, self.DOWN_LEFT, self.DOWN_RIGHT]:
                self.rect.y += self.moveSpeed
                dir = 'down'
            if move in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
                self.rect.x -= self.moveSpeed
                dir = 'left'
            if move in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
                self.rect.x += self.moveSpeed
                dir = 'right'

            self._setAnimationDirection(dir)
            self.image = self.animations[self.animationDirection][self.animationStep]
            self.rect.clamp_ip(self.playRect)

    def shoot(self, shoot):
        if shoot:
            if self.shootDelayRemaining <= 0:
                bullet = Bullet(self.engine, self.rect.x, self.rect.y, shoot, self.playRect)
                self.engine.add_bullet(bullet)
                self.shootDelayRemaining = self.shootDelay

    def update(self):
        self.shootDelayRemaining -= 1

        for sprite in pygame.sprite.spritecollide(self, self.engine.get_family_group(), False):
            sprite.collected()

    def zero(self):
        pass

    def reset(self):
        self.shootDelayRemaining = 0
        self.animationStep = 0
        self.animationDirection = 'down'

        self.image = self.animations[self.animationDirection][self.animationStep]

        self.rect = self.image.get_rect()
        self.rect.x = self.playRect.x + (self.playRect.width // 2)
        self.rect.y = self.playRect.y + (self.playRect.height // 2)

    def _setAnimationDirection(self, dir):
        if self.animationDirection == dir:
            self.animationStep += 1
            if self.animationStep >= len(self.animations[self.animationDirection]):
                self.animationStep = 0

        else:
            self.animationDirection = dir
            self.animationStep = 0
