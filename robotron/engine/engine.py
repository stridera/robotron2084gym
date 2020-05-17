import pygame

from ..sprites import Sprites


class Engine:
    def __init__(self, screen_size, playRect, waveInfo, startLevel=1, fps=0):
        self.playRect = playRect
        self.waveInfo = waveInfo
        self.defaultStartingLevel = startLevel - 1
        self.score = 0
        self.level = startLevel
        self.lives = 3
        self.extraLives = 0
        self.fps = fps

        pygame.init()
        pygame.display.set_caption('Robotron')
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(screen_size)
        self.font = pygame.font.Font(None, 30)

        self.sprites = Sprites(self)

        self.playerGroup = pygame.sprite.Group()  # Player and their bullets
        self.familyGroup = pygame.sprite.Group()  # Enemies and their bullets.
        self.enemyGroup = pygame.sprite.Group()  # Enemies and their bullets.
        self.toKillGroup = pygame.sprite.Group()  # Enemies that need to die to advance the level.
        self.allGroup = pygame.sprite.Group()  # All sprites on screen.

        self.toKillGroupTypes = [
            'Grunt'
        ]

        self.player = None
        self.playerBox = None

        self.familyCollected = 0

        self.initialize_level()

    def handle_input(self, move, shoot):
        """ Handle Player Input """
        if self.lives > 0:
            self.player.move(move)
            self.player.shoot(shoot)

    # State Management

    def initialize_level(self):
        for sprite in self.allGroup:
            sprite.kill()

        self.player = self.sprites.Player()
        self.add_player(self.player)

        self.familyCollected = 0
        levelData = self.waveInfo[self.level]
        (grunts, electrodes, hulks, brains, sphereoids, quarks, mommies, daddies, mikeys) = levelData

        for _ in range(mommies):
            self.add_family(self.sprites.Mommy())

        for _ in range(daddies):
            self.add_family(self.sprites.Daddy())

        for _ in range(mikeys):
            self.add_family(self.sprites.Mikey())

        for _ in range(grunts):
            self.add_enemy(self.sprites.Grunt())

        for _ in range(electrodes):
            self.add_enemy(self.sprites.Electrode())

        for _ in range(hulks):
            self.add_enemy(self.sprites.Hulk())

    def add_score(self, score):
        self.score += score

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
        return self.familyCollected

    def set_level(self, level):
        self.level = level
        self.initialize_level()

    def get_level(self):
        return self.level

    def get_play_area(self):
        return self.playRect

    def get_player_group(self):
        return self.playerGroup

    def get_family_group(self):
        return self.familyGroup

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
        pygame.draw.rect(self.screen, [238, 5, 8], self.playRect.inflate(15, 15), 5)
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
        self.allGroup.add(bullet)

    def add_family(self, family):
        self.familyGroup.add(family)
        self.allGroup.add(family)

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
        self.clock.tick(self.fps)

        # You start the game with 3 men and receive and additional man for every 25,000 points you get.
        if self.score // 25000 > self.extraLives:
            self.lives += 1
            self.extraLives += 1

        if self.lives > 0:
            self.allGroup.update()

            if pygame.sprite.spritecollide(self.player, self.enemyGroup, False):
                self.familyCollected = 0
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
        self.extraLives = 0

        self.initialize_level()
