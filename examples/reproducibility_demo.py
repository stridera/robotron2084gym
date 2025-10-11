#!/usr/bin/env python3
"""
Reproducibility demonstration for Robotron 2084 environment.

This script proves that using the same seed produces identical gameplay.
"""

from robotron import RobotronEnv
import numpy as np


def run_episode(env, seed, num_steps=100):
    """Run an episode and return trajectory."""
    obs, info = env.reset(seed=seed)

    trajectory = {
        'observations': [obs.copy()],
        'rewards': [],
        'scores': [info['score']],
        'positions': [info['data'][:5]]  # First 5 sprite positions
    }

    # Seed action space for deterministic action sampling
    action_rng = np.random.default_rng(seed)

    for _ in range(num_steps):
        action = action_rng.integers(0, env.action_space.n)
        obs, reward, terminated, truncated, info = env.step(action)

        trajectory['observations'].append(obs.copy())
        trajectory['rewards'].append(reward)
        trajectory['scores'].append(info['score'])
        trajectory['positions'].append(info['data'][:5])

        if terminated:
            break

    return trajectory


def main():
    print("Demonstrating reproducibility with seeding...\n")

    # Create two identical environments
    env1 = RobotronEnv(headless=True)
    env2 = RobotronEnv(headless=True)

    SEED = 42
    STEPS = 100

    # Run same episode twice
    print(f"Running episode 1 with seed={SEED}...")
    traj1 = run_episode(env1, seed=SEED, num_steps=STEPS)

    print(f"Running episode 2 with seed={SEED}...")
    traj2 = run_episode(env2, seed=SEED, num_steps=STEPS)

    # Compare trajectories
    print(f"\n=== Comparison Results ===")
    print(f"Episode length: {len(traj1['rewards'])} vs {len(traj2['rewards'])}")

    # Check observations
    obs_match = all(np.array_equal(o1, o2)
                   for o1, o2 in zip(traj1['observations'], traj2['observations']))
    print(f"Observations identical: {obs_match}")

    # Check rewards
    rewards_match = traj1['rewards'] == traj2['rewards']
    print(f"Rewards identical: {rewards_match}")

    # Check scores
    scores_match = traj1['scores'] == traj2['scores']
    print(f"Scores identical: {scores_match}")

    # Check sprite positions
    positions_match = traj1['positions'] == traj2['positions']
    print(f"Sprite positions identical: {positions_match}")

    if obs_match and rewards_match and scores_match and positions_match:
        print("\n✅ SUCCESS: Environment is fully deterministic!")
    else:
        print("\n❌ FAILED: Trajectories differ!")

    # Demonstrate different seed produces different results
    print(f"\n=== Different Seed Test ===")
    traj3 = run_episode(env1, seed=123, num_steps=STEPS)

    # Check if observations and positions differ
    obs_different = any(
        not np.array_equal(traj1['observations'][i], traj3['observations'][i])
        for i in range(min(len(traj1['observations']), len(traj3['observations'])))
    )
    pos_different = any(
        traj1['positions'][i] != traj3['positions'][i]
        for i in range(min(len(traj1['positions']), len(traj3['positions'])))
    )
    print(f"Different seed produces different observations: {obs_different}")
    print(f"Different seed produces different positions: {pos_different}")

    env1.close()
    env2.close()


if __name__ == "__main__":
    main()
