#!/usr/bin/env python3
"""
Basic usage example for Robotron 2084 Gymnasium environment.

This script demonstrates:
- Creating an environment
- Running a simple random agent
- Accessing state information
"""

from robotron import RobotronEnv
import numpy as np


def main():
    # Create environment with standard settings
    env = RobotronEnv(
        level=1,           # Start at level 1
        lives=3,           # 3 lives
        fps=30,            # 30 FPS for visibility
        headless=False,    # Show the game window
        render_mode='human'
    )

    print(f"Action space: {env.action_space}")
    print(f"Observation space: {env.observation_space}")

    # Run for 3 episodes
    for episode in range(3):
        print(f"\n=== Episode {episode + 1} ===")
        obs, info = env.reset()
        total_reward = 0
        steps = 0

        terminated = False
        while not terminated:
            # Random action
            action = env.action_space.sample()

            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)

            total_reward += reward
            steps += 1

            # Print progress every 100 steps
            if steps % 100 == 0:
                print(f"Step {steps}: Score={info['score']}, Lives={info['lives']}, "
                      f"Level={info['level']}, Family={info['family']}")

        print(f"Episode finished: {steps} steps, total reward: {total_reward:.2f}")
        print(f"Final score: {info['score']}, reached level: {info['level']}")

    env.close()


if __name__ == "__main__":
    main()
