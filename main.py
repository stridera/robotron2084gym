#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  ______  _____  ______   _____  _______  ______  _____  __   _
 |_____/ |     | |_____] |     |    |    |_____/ |     | | \  |
 |    \_ |_____| |_____] |_____|    |    |    \_ |_____| |  \_|

    This file allows humans to play the game.
"""


import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_q, K_RETURN, K_a, K_s, K_d, K_w, K_j, K_k, K_l, K_i

import game


class Input():
    """ Gets imput from a controller if attached. """
    UP = 1  # 1 << 0
    DOWN = 2  # 1 << 1
    RIGHT = 4  # 1 << 2
    LEFT = 8  # 1 << 3

    UPDOWNAXIS = 1
    LEFTRIGHTAXIS = 0
    ABUTTON = 0
    BBUTTON = 1
    XBUTTON = 2
    YBUTTON = 3
    BACKBUTTON = 6
    STARTBUTTON = 7

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.has_joystick = False

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)

            print("Using joystick: ", self.joystick.get_name())
            self.has_joystick = True
            self.joystick.init()
        else:
            print("Using keyboard as input.")

    def __bin_to_cardinal(self, direction):
        """ Convert from the int direction to a cardinal direction """
        response = 0

        if direction == 0:
            response = 0
        elif direction == self.UP:
            response = 1
        elif direction == self.UP | self.RIGHT:
            response = 2
        elif direction == self.RIGHT:
            response = 3
        elif direction == self.DOWN | self.RIGHT:
            response = 4
        elif direction == self.DOWN:
            response = 5
        elif direction == self.DOWN | self.LEFT:
            response = 6
        elif direction == self.LEFT:
            response = 7
        elif direction == self.UP | self.LEFT:
            response = 8
        else:
            print("Unknown input", direction)
            response = 0

        return response

    def read_controller(self):
        """ Read value from controller """

        if not self.has_joystick:
            raise Exception('Joystick not attached.')

        pygame.event.pump()

        start = self.joystick.get_button(self.STARTBUTTON)
        back = self.joystick.get_button(self.BACKBUTTON)
        axis0 = self.joystick.get_axis(self.UPDOWNAXIS)
        axis1 = self.joystick.get_axis(self.LEFTRIGHTAXIS)

        left = 0
        if axis0 > 0.5:
            left |= self.DOWN
        if axis0 < -0.5:
            left |= self.UP
        if axis1 > 0.5:
            left |= self.RIGHT
        if axis1 < -0.5:
            left |= self.LEFT

        a_button = self.joystick.get_button(self.ABUTTON)
        b_button = self.joystick.get_button(self.BBUTTON)
        x_button = self.joystick.get_button(self.XBUTTON)
        y_button = self.joystick.get_button(self.YBUTTON)

        right = 0
        if a_button:
            right |= self.DOWN
        if b_button:
            right |= self.RIGHT
        if y_button:
            right |= self.UP
        if x_button:
            right |= self.LEFT

        return (
            self.__bin_to_cardinal(left),
            self.__bin_to_cardinal(right),
            start,
            back,
        )

    def attached(self):
        """ Is controller attached? """
        return self.has_joystick

    def get(self):
        if self.attached():
            return self.read_controller()

        pygame.event.pump()

        left = 0
        right = 0
        back = False
        start = False
        for event in pygame.event.get():
            if event.type == QUIT:
                back = True

        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE] or keys[K_q]:
            back = True

        if keys[K_RETURN]:
            start = True

        if keys[K_w]:
            left |= self.UP
        elif keys[K_s]:
            left |= self.DOWN
        if keys[K_d]:
            left |= self.RIGHT
        elif keys[K_a]:
            left |= self.LEFT

        if keys[K_i]:
            right |= self.UP
        elif keys[K_k]:
            right |= self.DOWN
        if keys[K_j]:
            right |= self.LEFT
        elif keys[K_l]:
            right |= self.RIGHT

        return (
            self.__bin_to_cardinal(left),
            self.__bin_to_cardinal(right),
            start,
            back,
        )


def main():
    env = game.Robotron()
    input = Input()

    image = env.reset()
    try:
        while True:
            (left, right, start, back) = input.get()

            if back:
                break

            if start:
                env.reset()

            action = left * 8 + right
            image, reward, done, info = env.step(action)

    except (KeyboardInterrupt):
        print("Interrupt detected.  Exiting...")

    print("Goodbye!")


if __name__ == "__main__":
    main()
