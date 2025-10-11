"""Basic tests for the Robotron environment."""
import numpy as np
import pytest
from robotron import RobotronEnv


class TestEnvironmentBasics:
    """Test basic environment functionality."""

    def test_environment_creation(self):
        """Test that environment can be created."""
        env = RobotronEnv(headless=True)
        assert env is not None
        env.close()

    def test_reset(self):
        """Test environment reset."""
        env = RobotronEnv(headless=True)
        obs, info = env.reset(seed=42)

        # Check observation
        assert obs.shape == env.observation_space.shape
        assert obs.dtype == np.uint8

        # Check info dict
        assert 'score' in info
        assert 'level' in info
        assert 'lives' in info
        assert 'family' in info
        assert 'data' in info

        # Check initial values
        assert info['score'] == 0
        assert info['lives'] == 3
        assert info['level'] == 0

        env.close()

    def test_step(self):
        """Test environment step."""
        env = RobotronEnv(headless=True)
        env.reset(seed=42)

        obs, reward, terminated, truncated, info = env.step(0)

        # Check return types
        assert obs.shape == env.observation_space.shape
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

        env.close()

    def test_action_space(self):
        """Test action space is correct."""
        # Default action space (9x9 = 81)
        env = RobotronEnv(headless=True)
        assert env.action_space.n == 81
        env.close()

        # Always move action space (8x8 = 64)
        env = RobotronEnv(headless=True, always_move=True)
        assert env.action_space.n == 64
        env.close()

    def test_observation_space(self):
        """Test observation space is correct."""
        env = RobotronEnv(headless=True)

        # Should be RGB image
        assert len(env.observation_space.shape) == 3
        assert env.observation_space.shape[2] == 3  # RGB channels
        assert env.observation_space.dtype == np.uint8

        env.close()


class TestDeterminism:
    """Test deterministic seeding."""

    def test_same_seed_same_results(self):
        """Test that same seed produces identical results."""
        env1 = RobotronEnv(headless=True)
        env2 = RobotronEnv(headless=True)

        obs1, info1 = env1.reset(seed=42)
        obs2, info2 = env2.reset(seed=42)

        # Check observations match
        assert np.array_equal(obs1, obs2)

        # Check info matches
        assert info1['score'] == info2['score']
        assert info1['lives'] == info2['lives']
        assert info1['level'] == info2['level']

        # Take steps and verify they match
        for _ in range(10):
            obs1, r1, d1, t1, info1 = env1.step(0)
            obs2, r2, d2, t2, info2 = env2.step(0)

            assert np.array_equal(obs1, obs2)
            assert r1 == r2
            assert d1 == d2
            assert info1['score'] == info2['score']

        env1.close()
        env2.close()

    def test_different_seed_different_results(self):
        """Test that different seeds produce different results."""
        env1 = RobotronEnv(headless=True)
        env2 = RobotronEnv(headless=True)

        obs1, info1 = env1.reset(seed=42)
        obs2, info2 = env2.reset(seed=123)

        # Sprite positions should differ
        assert info1['data'] != info2['data']

        env1.close()
        env2.close()


class TestHeadlessMode:
    """Test headless mode rendering."""

    def test_headless_returns_observations(self):
        """Test that headless mode returns actual rendered observations."""
        env = RobotronEnv(headless=True)
        obs, info = env.reset(seed=42)

        # Should have non-zero pixels (actual rendering)
        assert np.count_nonzero(obs) > 0

        # Should have sprites
        assert len(info['data']) > 0

        env.close()

    def test_headless_performance(self):
        """Test that headless mode is reasonably fast."""
        import time

        env = RobotronEnv(headless=True, fps=0)
        env.reset(seed=42)

        start = time.time()
        steps = 100
        for _ in range(steps):
            obs, reward, done, trunc, info = env.step(env.action_space.sample())
            if done:
                env.reset()

        elapsed = time.time() - start
        fps = steps / elapsed

        # Should be at least 50 FPS (very conservative)
        assert fps > 50, f"Expected >50 FPS, got {fps:.1f} FPS"

        env.close()


class TestMetadata:
    """Test Gymnasium metadata compliance."""

    def test_metadata_format(self):
        """Test that metadata is in correct Gymnasium format."""
        env = RobotronEnv(headless=True)

        assert 'render_modes' in env.metadata
        assert 'render_fps' in env.metadata
        assert isinstance(env.metadata['render_modes'], list)
        assert 'human' in env.metadata['render_modes']
        assert 'rgb_array' in env.metadata['render_modes']

        env.close()
