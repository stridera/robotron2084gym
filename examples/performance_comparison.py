#!/usr/bin/env python3
"""
Performance comparison: headless vs. rendered mode.

This script demonstrates the performance of different rendering modes:
- Headless: Off-screen rendering (fast + visual observations)
- Rendered: Display window (slower but visible)
- FPS-limited: Capped at specific frame rate
"""

from robotron import RobotronEnv
import time


def benchmark_env(env, num_steps=1000):
    """Benchmark environment for a given number of steps."""
    obs, info = env.reset(seed=42)

    start_time = time.time()

    for _ in range(num_steps):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        if terminated:
            obs, info = env.reset()

    elapsed = time.time() - start_time
    fps = num_steps / elapsed

    return elapsed, fps


def main():
    NUM_STEPS = 1000

    print(f"Benchmarking {NUM_STEPS} steps...\n")

    # Test 1: Headless mode
    print("Test 1: Headless mode (off-screen rendering)")
    env_headless = RobotronEnv(
        fps=0,
        headless=True,
        always_move=True
    )
    time_headless, fps_headless = benchmark_env(env_headless, NUM_STEPS)
    print(f"  Time: {time_headless:.2f}s")
    print(f"  FPS: {fps_headless:.1f}")
    print(f"  Note: Still returns full RGB observations!")
    env_headless.close()

    # Test 2: Rendered mode
    print("\nTest 2: Rendered mode (with display)")
    env_rendered = RobotronEnv(
        fps=0,
        headless=False,
        always_move=True,
        render_mode='human'
    )
    time_rendered, fps_rendered = benchmark_env(env_rendered, NUM_STEPS)
    print(f"  Time: {time_rendered:.2f}s")
    print(f"  FPS: {fps_rendered:.1f}")
    env_rendered.close()

    # Test 3: Rendered with frame limiting
    print("\nTest 3: Rendered with 30 FPS limit")
    env_limited = RobotronEnv(
        fps=30,
        headless=False,
        always_move=True,
        render_mode='human'
    )
    time_limited, fps_limited = benchmark_env(env_limited, NUM_STEPS)
    print(f"  Time: {time_limited:.2f}s")
    print(f"  FPS: {fps_limited:.1f}")
    env_limited.close()

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    speedup = fps_headless / fps_rendered
    print(f"Headless speedup: {speedup:.1f}x faster than rendered")
    print(f"\nRecommendation for training:")
    print(f"  - Use headless=True, fps=0 for maximum speed")
    print(f"  - Expected: ~{fps_headless:.0f} FPS on this machine")


if __name__ == "__main__":
    main()
