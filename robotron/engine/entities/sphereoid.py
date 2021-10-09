import random
from .enforcer import Enforcer
from .generator import Generator


class Sphereoid(Generator):
    def get_animations(self):
        return self.get_engine().get_sprites([
            'sphereoid1', 'sphereoid2', 'sphereoid3', 'sphereoid4',
            'sphereoid5', 'sphereoid6', 'sphereoid7', 'sphereoid8'
        ])

    def get_spawn(self):
        return Enforcer(self.engine, xy=self.rect.center)

    def update_curvature_and_countdowns(self):
        self.moveCurvature.x = random.randint(-50, 50) / 1000
        self.moveCurvature.y = random.randint(-50, 50) / 1000
        self.moveDelay = random.randrange(10, 32)

    def move(self):
        """ Sphereoids """
        self.moveDelay -= 1
        if self.moveDelay == 0:
            self.update_curvature_and_countdowns()

        self.moveDeltas.x = min(self.SPEED, max(-self.SPEED, self.moveDeltas.x + self.SPEED * self.moveCurvature.x))
        self.moveDeltas.y = min(self.SPEED, max(-self.SPEED, self.moveDeltas.y + self.SPEED * self.moveCurvature.y))
        self.rect.center += self.moveDeltas
        self.rect.clamp_ip(self.playRect)

    def reset(self):
        super().reset()
        self.update_curvature_and_countdowns()
