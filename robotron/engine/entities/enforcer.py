import random
import pygame

from .base import Base


class EnforcerBullet(Base):
    """
    Bullets shot from the Enforcer.
    """

    MAX_SPEED = 30
    DEFAULT_TIME_TO_LIVE = 50

    def setup(self):
        self.timeToLive = self.DEFAULT_TIME_TO_LIVE
        self.vector = None

    def get_trajectory(self):
        if not self.vector:
            engine = self.get_engine()
            distanceToPlayer = self.get_distance_to_player()
            max_distance = engine.get_play_area_distance()
            speed = ((distanceToPlayer * self.MAX_SPEED) / max_distance) + 1
            player_rect = engine.player.rect
            tx = random.randint(player_rect.left - 10, player_rect.right + 10)
            ty = random.randint(player_rect.top - 10, player_rect.bottom + 10)
            self.vector = (pygame.Vector2(tx, ty) - pygame.Vector2(self.rect.center)).normalize() * speed
            self.randomVector = pygame.Vector2(random.random(), random.random())
        else:
            self.randomVector *= 1.01

        return self.vector + self.randomVector

    def get_animations(self):
        """
        Update the current image.  Right now I draw it every cycle.  This is because in the
        game they change colors and I was going to add that, but for now, we just have black
        and white.
        """
        weight = 2
        width = height = 16
        image1 = pygame.Surface([width, height]).convert()
        pygame.draw.line(image1, [255, 255, 255], (width, 0), (0, height), weight)
        pygame.draw.line(image1, [255, 255, 255], (0, 0), (width, height), weight)
        image2 = pygame.Surface([width, height]).convert()
        pygame.draw.line(image2, [255, 255, 255], (width // 2, 0), (width // 2, height), weight)
        pygame.draw.line(image2, [255, 255, 255], (0, height // 2), (width, height // 2), weight)
        return [image1, image2]

    def update(self):
        if self.timeToLive % 3 == 0:
            self.update_animation()
        self.rect.center += self.get_trajectory()
        self.rect.clamp_ip(self.playRect)

        self.timeToLive -= 1
        if self.timeToLive <= 0:
            self.kill()

    def zero(self):
        self.kill()

    def reset(self):
        self.kill()


class Enforcer(Base):
    """
    Enforcer Enemy

    Behavior:
        Spawned by the Sphereoids, the enforcers will fly around and shoot you.  In an
        attempt to shoot at where you will be instead of where you are at, they shoot at
        a 10pixel window around the player.
    """

    MAX_SPEED = 20
    MIN_SPEED = 0.2

    def get_animations(self):
        return self.get_engine().get_sprites(
            ['enforcer2', 'enforcer3', 'enforcer4', 'enforcer5', 'enforcer6', 'enforcer1'])

    def setup(self):
        self.animationStep = 0
        self.animationDelay = 0
        self.update_animation()

        self.rect = self.image.get_rect()
        self.active = 0

        self.max_distance = self.get_engine().get_play_area_distance()
        self.offset_update = 0
        self.random_offset = 0
        self.shootDelay = random.randint(10, 30)

    def update(self):
        self.update_animation()
        self.move()
        self.shoot()

    def update_animation(self):
        """
        Enforcers cycle through all animations until they hit the end one.  (Basically growing up.)  Once
        they're fully grown, the sprite doesn't change.
        """
        if self.animationStep < len(self.animations):
            if self.animationDelay == 0:
                self.image = self.animations[self.animationStep]
                self.animationStep += 1
                self.animationDelay = 3
            else:
                self.animationDelay -= 1
        else:
            self.active = True

    def move(self):
        """
        This isn't an exact copy of the game, but close enough.  They move toward the player with a speed that is
        directly proportional to the distance to the player.  (The closer they are, the slower they go.)  They
        also get a random velocity offest that gives them random movements.  This means they can move away from
        the player at times.
        """
        if self.active:
            if self.offset_update <= 0:
                self.random_offset = random.randint(-5, 1)
                self.offset_update = random.randint(10, 30)

            self.offset_update -= 1

            distanceToPlayer = self.get_distance_to_player()
            speed = ((distanceToPlayer * self.MAX_SPEED) / self.max_distance) + 1
            self.move_toward_player(speed + self.random_offset)
            self.rect.clamp_ip(self.playRect)

    def shoot(self):
        """
        Enforcers shoot little sparks toward the player.  They target a 10 pixel range around the player so it's
        possible it can appear like they're guessing where you'll move.  The speed is also proportional to the
        distance from the player.  The farther away means the faster they go.  There is also a random velocity
        added to each bullet each frame which can make them appear to curve.
        """
        self.shootDelay -= 1
        if self.shootDelay <= 0:
            self.shootDelay = random.randint(10, 30)
            self.engine.add_enemy(EnforcerBullet(self.engine, xy=self.rect.center))

    def reset(self):
        self.kill()
