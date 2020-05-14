import pygame

from ..sprites import Sprites


class Engine:
    def __init__(self, screen_size, playRect, waveInfo, startLevel=1):
        self.playRect = playRect
        self.waveInfo = waveInfo
        self.defaultStartingLevel = startLevel - 1
        self.score = 0
        self.level = startLevel
        self.lives = 3

        pygame.init()
        pygame.display.set_caption('Robotron')
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(screen_size)
        self.font = pygame.font.Font(None, 30)

        self.sprites = Sprites(self)

        self.playerGroup = pygame.sprite.Group()  # Player and their bullets
        self.enemyGroup = pygame.sprite.Group()  # Enemies and their bullets.
        self.toKillGroup = pygame.sprite.Group()  # Enemies that need to die to advance the level.
        self.allGroup = pygame.sprite.Group()  # All sprites on screen.

        self.toKillGroupTypes = [
            'Grunt'
        ]

        self.player = None
        self.playerBox = None

        self.initialize_level()

    def handle_input(self, move, shoot):
        """ Handle Player Input """
        if self.lives > 0:
            self.player.move(move)
            self.player.shoot(shoot)

    # State Management

    def add_score(self, score):
        self.score += score

    def get_score(self):
        return self.score

    def set_level(self, level):
        self.level = level
        self.initialize_level()

    def get_level(self):
        return self.level

    def get_play_area(self):
        return self.playRect

    def initialize_level(self):
        for sprite in self.allGroup:
            sprite.kill()

        self.player = self.sprites.Player()
        self.add_player(self.player)

        levelData = self.waveInfo[self.level]
        (grunts, electrodes, hulks, brains, sphereoids, quarks, mommies, daddies, mikeys) = levelData

        for _ in range(grunts):
            self.add_enemy(self.sprites.Grunt())

    def get_player_group(self):
        return self.playerGroup

    def get_enemy_group(self):
        return self.enemyGroup

    def get_all_group(self):
        return self.allGroup

    # Sprite Management

    def get_player_box(self):
        """ Safe area around player to not place enemies on load """
        if self.playerBox is None:
            (x, y) = self.player.rect.center
            (w, h) = (self.playRect.width // 3, self.playRect.height // 3)
            self.playerBox = pygame.Rect(x - w // 2, y - h // 2, w, h)

        return self.playerBox

    def add_background(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, [238, 5, 8], self.playRect, 5)
        # pygame.draw.rect(self.screen, [5, 238, 8], self.get_player_box(), 5)

    def add_info(self):
        text = self.font.render(
            f'Score: {self.score} Level: {self.level + 1} Lives: {self.lives}',
            True,
            (255, 255, 255),
            (0, 0, 0))
        self.screen.blit(text, (self.playRect.x, self.playRect.y - 40))

    def add_player(self, player):
        self.player = player
        self.playerGroup.add(player)
        self.allGroup.add(player)

    def add_bullet(self, bullet):
        self.playerGroup.add(bullet)
        self.allGroup.add(bullet)

    def add_enemy(self, enemy):
        self.enemyGroup.add(enemy)
        self.allGroup.add(enemy)

        if enemy.__class__.__name__ in self.toKillGroupTypes:
            self.toKillGroup.add(enemy)

    def get_image(self):
        pygame.surfarray.array3d(pygame.display.get_surface())

    # Lifecycle Management

    def update(self):
        pygame.event.pump()
        self.clock.tick(30)

        if self.lives > 0:
            self.allGroup.update()

            if pygame.sprite.spritecollide(self.player, self.enemyGroup, False):
                self.lives -= 1
                if self.lives > 0:
                    for sprite in self.allGroup:
                        sprite.zero()
                    for sprite in self.allGroup:
                        sprite.reset()

            if not self.toKillGroup:
                self.level += 1
                self.initialize_level()

        return (self.score, self.lives, self.lives == 0)

    def draw(self):
        self.add_background()
        self.add_info()
        self.allGroup.draw(self.screen)
        pygame.display.update()

    def reset(self):
        self.score = 0
        self.level = self.defaultStartingLevel
        self.lives = 3

        self.initialize_level()
