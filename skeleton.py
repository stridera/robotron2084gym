"""
Robotron Skeleton Runner Code

This is the simplest way to run the game.  It will run the game at 30 fps and will provide random
actions to the game.  It will print out the score, level, lives, reward, and if the player is dead.
It will also print out the family remaining and the objects on the board.
Objects can be:
    Player
    Mommy
    Daddy
    Mikey
    Tank
    TankShell
    Grunt
    Electrode
    Hulk
    Bullet
    CruiseMissile
    Brain
    Enforcer
    EnforcerBullet
    Sphereoid
    Quark
"""

import argparse

from robotron import RobotronEnv


def main(starting_level: int = 1, fps: int = 30, godmode: bool = False):
    env = RobotronEnv(starting_level, fps, godmode, headless=False)
    board_size = env.get_board_size()
    print(f"Board Size: {board_size}")  # Default Board Size: (665, 492)
    env.reset()
    while True:
        _image, reward, isDead, data = env.step(env.action_space.sample())
        score, level, lives, family, data = data.values()
        print(f"Score: {score} | Level: {level} | Lives: {lives} | Reward: {reward} | Dead: {isDead}")
        print(f"Family Remaining: {family} | Objects: {data}")
        """
        Should look like:
        Score: 0 | Level: 1 | Lives: 3 | Reward: 0.0 | Dead: False
            Family Remaining: 2 | Objects: [(337, 246, 'Player'), (38, 292, 'Mommy'), (578, 223, 'Daddy'), 
            (489, 15, 'Grunt'), (7, 439, 'Grunt'), (613, 241, 'Grunt'), (195, 137, 'Electrode'), 
            (136, 123, 'Electrode'), (214, 161, 'Electrode'), (187, 334, 'Electrode'), (625, 186, 'Electrode'), 
            (352, 261, 'Bullet')]
        """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rainbow')
    parser.add_argument('--level', type=int, default=1, help='Start Level')
    parser.add_argument('--fps', type=int, default=30, help='FPS')
    parser.add_argument('--godmode', action='store_true', help='Enable GOD Mode (Can\'t die.)')

    args = parser.parse_args()
    main(args.level, args.fps, args.godmode)
