# Robotron 2084 Examples

This directory contains example scripts demonstrating various features of the Robotron 2084 Gymnasium environment.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the fundamental usage of the environment:
- Creating an environment
- Running episodes with random actions
- Accessing state information from the `info` dict

```bash
python examples/basic_usage.py
```

### 2. Reproducibility Demo (`reproducibility_demo.py`)

Proves that the environment is fully deterministic when seeded:
- Runs identical episodes with the same seed
- Compares observations, rewards, scores, and sprite positions
- Shows that different seeds produce different results

```bash
python examples/reproducibility_demo.py
```

**Expected output:**
```
✅ SUCCESS: Environment is fully deterministic!
```

### 3. Performance Comparison (`performance_comparison.py`)

Benchmarks different rendering modes to show performance differences:
- Headless mode (fastest, ~30-50% speedup)
- Rendered mode (with display)
- Frame-limited mode (30 FPS cap)

```bash
python examples/performance_comparison.py
```

### 4. Custom Configuration (`custom_config.py`)

Shows how to create and use custom configuration files:
- Creating a YAML config programmatically
- Loading custom difficulty settings
- Modifying enemy behavior

```bash
python examples/custom_config.py
```

## Requirements

All examples require the robotron package to be installed:

```bash
pip install -r ../requirements.txt
```

## Tips for RL Training

Based on the performance comparison, for optimal training speed:

```python
env = RobotronEnv(
    fps=0,              # No frame limiting
    headless=True,      # Skip rendering (~30-50% faster)
    always_move=True,   # Reduced action space (64 vs 81)
    render_mode=None,   # No render output
)
```

For reproducible experiments, always use seeding:

```python
obs, info = env.reset(seed=42)
```
