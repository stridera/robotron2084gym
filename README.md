# Robotron 2084 Gym Environment

This is a remake of the XBox (and older, using xbox graphics) game of Robotron 2084.

![Robotron Game](resources/robotron.png "Robotron 2084")

Working on simulating the XBox look and feel in an attempt to train a model and then test it on the console itself.

(See [my robotron player](https://github.com/stridera/robotron))

**Quick Links:**
- 📖 [Quick Start Guide](QUICKSTART.md) - Get running in 60 seconds
- 💻 [Examples](examples/) - Practical code samples
- 🏗️ [Architecture](CLAUDE.md) - Developer documentation
- 🤝 [Contributing](CONTRIBUTING.md) - Development guide

## Features

✅ **Gymnasium-compliant** - Works with modern RL frameworks
✅ **Fully deterministic** - Seeded reproducibility for experiments
✅ **Performance optimized** - Headless mode with off-screen rendering
✅ **Visual observations** - Full RGB observations even in headless mode
✅ **Type-safe** - Comprehensive type hints throughout
✅ **Well-tested** - Examples and test coverage
✅ **Configurable** - YAML-based game parameters

## Installation

### Option 1: Poetry (Recommended)

[Poetry](https://python-poetry.org/) provides better dependency management and virtual environment handling:

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Clone repository
git clone git@github.com:stridera/robotron-2084.git
cd robotron-2084/

# Install dependencies (creates virtual environment automatically)
poetry install

# Run the game
poetry run python main.py

# Or activate the virtual environment
poetry shell
python main.py
```

### Option 2: pip

Traditional installation using pip:

```bash
# Install Python 3.10+ (Ubuntu example)
sudo apt install python3.10 python3.10-venv

# Clone repository
git clone git@github.com:stridera/robotron-2084.git
cd robotron-2084/

# Create and activate virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the game
python main.py
```

### Requirements

- **Python:** 3.10, 3.11, or 3.12
- **OS:** Linux, macOS, or Windows (with WSL recommended)

## Configs

Everything is configurable. You can either modify `robotron/engine/config.yaml` directly or copy it and provide it to the engine via the `config_path` argument. You can use this to change the number of enemies per level, how fast enemies move, or how many bullets/enemies they spawn.

The current one is optimized for machine learning and has some changes from live. (Like, we don't gain extra lives.)
The `config.yaml.default` file is as close to the real game as I could make it. Feel free to copy it over to get back those functions.

## Gymnasium Environment

This environment follows the [Gymnasium](https://gymnasium.farama.org/) API (the maintained successor to OpenAI Gym). It's fully compatible with modern RL frameworks.

### Quick Start

```python
from robotron import RobotronEnv

# Create environment for RL training
env = RobotronEnv(
    level=1,              # Starting level
    lives=3,              # Number of lives
    fps=0,                # 0 = max speed for training
    headless=True,        # No display (faster training)
    always_move=True,     # Reduced action space (64 vs 81)
    render_mode=None,     # 'human' or 'rgb_array'
)

# Standard Gymnasium API
obs, info = env.reset(seed=42)  # Seeded for reproducibility
terminated = False

while not terminated:
    action = env.action_space.sample()  # Your agent here
    obs, reward, terminated, truncated, info = env.step(action)

env.close()
```

### Environment Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | int | 1 | Starting level (1-40) |
| `lives` | int | 3 | Number of lives |
| `fps` | int | 0 | Frames per second (0 = unlimited, best for training) |
| `headless` | bool | True | Off-screen rendering (no display window, still returns observations) |
| `always_move` | bool | False | Reduce action space from 81 to 64 (no-op removed) |
| `godmode` | bool | False | Invincibility (for debugging) |
| `config_path` | str | None | Path to custom config YAML |
| `render_mode` | str | None | 'human' or 'rgb_array' |
| `seed` | int | None | Random seed (pass to `reset()` instead) |

### Action Space

**Default (Discrete 81):**
- Combines movement (9 directions) and shooting (9 directions)
- Action encoding: `action = movement * 9 + shooting`
- Directions: 0=None, 1=Up, 2=UpRight, 3=Right, 4=DownRight, 5=Down, 6=DownLeft, 7=Left, 8=UpLeft

**With `always_move=True` (Discrete 64):**
- Removes no-movement option for reduced action space
- Action encoding: `action = movement * 8 + shooting` (movements and shooting are 0-7)

### Observation Space

- **Type:** `Box(0, 255, (height, width, 3), uint8)`
- **Shape:** RGB image of play area (default: 492×665×3)
- **Values:** Cropped view of the game arena

### Rewards

- **Score delta:** `(new_score - old_score) / 100.0`
- **Death penalty:** `-1.0`
- **Family bonus:** Progressive (1k, 2k, 3k, 4k, 5k max per level)

### Info Dictionary

Returns detailed state information:

```python
{
    'score': int,        # Current score
    'level': int,        # Current level (0-indexed)
    'lives': int,        # Lives remaining
    'family': int,       # Family members remaining
    'data': List[Tuple]  # [(x, y, sprite_name), ...] for all sprites
}
```

### API Methods

#### `reset(seed=None, options=None)`

Resets the environment to initial state.

**Arguments:**
- `seed` (int, optional): Random seed for reproducibility
- `options` (dict, optional): Additional reset options

**Returns:**
- `observation` (ndarray): Initial game state image
- `info` (dict): Initial state information

**Example:**
```python
obs, info = env.reset(seed=42)  # Reproducible reset
```

#### `step(action)`

Execute one game step with the given action.

**Arguments:**
- `action` (int): Action in range [0, action_space.n)

**Returns:**
- `observation` (ndarray): Game state image
- `reward` (float): Reward for this step
- `terminated` (bool): True if game over (all lives lost)
- `truncated` (bool): Always False (no time limit)
- `info` (dict): State information

**Example:**
```python
obs, reward, terminated, truncated, info = env.step(action)
```

#### `render()`

Render the environment (if `render_mode` is set).

**Returns:**
- `ndarray` if `render_mode='rgb_array'`
- `None` if `render_mode='human'` (displays via pygame)

#### `close()`

Clean up environment resources.

```python
env.close()  # Important: call when done!
```

### Reproducibility & Seeding

The environment supports full deterministic reproducibility:

```python
# Create two identical environments
env1 = RobotronEnv(headless=True)
env2 = RobotronEnv(headless=True)

# Reset with same seed
obs1, _ = env1.reset(seed=42)
obs2, _ = env2.reset(seed=42)

# Same actions produce identical results
for _ in range(100):
    action = env1.action_space.sample()
    obs1, r1, d1, t1, info1 = env1.step(action)
    obs2, r2, d2, t2, info2 = env2.step(action)
    assert np.array_equal(obs1, obs2)  # Identical observations
```

### Performance Tips

For maximum training speed:

```python
env = RobotronEnv(
    fps=0,              # No frame rate limiting
    headless=True,      # Off-screen rendering (no display window)
    always_move=True,   # Smaller action space
)
```

**Note:** Headless mode renders to an off-screen surface, so you still get full visual observations for training without the overhead of displaying to screen.

### Advanced: Custom Configuration

Create a custom `config.yaml` to modify game behavior:

```python
env = RobotronEnv(config_path='path/to/custom_config.yaml')
```

See `robotron/engine/config.yaml` for all available options.

## Examples

Check out the [`examples/`](examples/) directory for practical code samples:

- **`basic_usage.py`** - Getting started with the environment
- **`reproducibility_demo.py`** - Proving deterministic seeding works
- **`performance_comparison.py`** - Benchmarking headless vs. rendered modes
- **`custom_config.py`** - Creating custom game configurations

Run any example:
```bash
python examples/basic_usage.py
```

## Todo

- [x] Create a pygame screen and draw the play area square.
- [x] Read the stylesheet and setup sprites.
- [x] Parse the wave info.
- [x] Add the player to the center.
  - [x] Allow him to run around and shoot bullets.
- [x] Add Grunts.
  - [x] Grunts run toward the player and they move sporadically.
  - [ ] Grunts speed up as the time advances on a stage.
- [x] Add Electrodes.
  - [x] Unlike companion cubes, Electrodes will stab you. Electrodes kill grunts and player.
- [x] Add Family Members.
- [x] Add Hulks.
- [x] Add Brains.
- [x] Add Spheroids.
- [x] Add Enforcers.
- [x] Add Quarks.
- [x] Add Tanks.
- [x] Properly handle rolling over level 40. (Waves restart at 21 and repeat.)
- [ ] Add flashing effects similar to in game.
- [ ] Add warp-in/warp-out effects.

## Attributions and Thanks

- Robotron 2084. Developed by Eugene Jarvis and Larry DeMar. Published by Williams Electronics.
- Sprite Sheet and definitions are from [Sean Riddle's Ripper page](https://seanriddle.com/ripper.html).
- Notes, score info, etc from [IGN's Robotron 2084 FAQ](https://www.ign.com/faqs/2005/robotron-2084-general-faq-430788)
