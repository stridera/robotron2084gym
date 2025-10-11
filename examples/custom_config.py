#!/usr/bin/env python3
"""
Custom configuration example.

This script demonstrates how to create and use a custom config file
to modify game behavior.
"""

from robotron import RobotronEnv
import yaml
import tempfile
import os


def create_custom_config():
    """Create a custom config with easier difficulty."""
    config = {
        'screen_size': [1280, 720],
        'play_area': [116, 309, 608, 974],
        'resource_path': 'resources/',
        'extra_life_score': 25000,  # Gain extra lives

        # Easier first level
        'waves': [
            [5, 2, 0, 0, 0, 0, 1, 1, 0],  # Fewer grunts & electrodes
        ],

        # Slower, weaker enemies
        'grunt': {
            'score': 100,
            'speed': 5,  # Slower than default (7)
            'move_delay': [10, 30]  # Move less frequently
        },
        'electrode': {
            'score': 25
        },
        'hulk': {
            'score': 0
        },
        'brain': {
            'score': 500,
            'speed': 0.5,  # Much slower
            'use_mikey_bug': True,
            'programming_time': 60,
            'programming_offset': 5,
            'shoot_delays': [100, 800]  # Shoot less often
        },
        'family': {
            'speed': 4,
            'move_delay': 5,
            'score': [100, 100, 100, 100, 100]
        },
    }

    # Write to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()

    return temp_file.name


def main():
    print("Demonstrating custom configuration...\n")

    # Create custom config
    custom_config_path = create_custom_config()
    print(f"Created custom config: {custom_config_path}")

    try:
        # Create environment with custom config
        env = RobotronEnv(
            config_path=custom_config_path,
            headless=False,
            fps=30,
            render_mode='human'
        )

        print("\nCustom configuration loaded!")
        print("Playing with easier difficulty (fewer, slower enemies)")
        print("Press Ctrl+C to stop\n")

        # Run a few episodes
        for episode in range(3):
            obs, info = env.reset()
            print(f"\n=== Episode {episode + 1} ===")

            terminated = False
            steps = 0

            while not terminated and steps < 500:
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                steps += 1

            print(f"Survived {steps} steps, score: {info['score']}")

        env.close()

    finally:
        # Clean up temporary file
        os.unlink(custom_config_path)
        print(f"\nCleaned up temporary config file")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
