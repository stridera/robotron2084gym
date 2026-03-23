# Robotron 2084 - Quick Start Guide

## Installation

```bash
# Poetry (recommended)
poetry install && poetry shell

# Or pip
pip install -r requirements.txt
```

## Play as a Human

```bash
python main.py                    # Default: level 1, 3 lives, 30 fps
python main.py --level 5          # Start at level 5
python main.py --lives 9          # 9 lives
python main.py --fps 60           # 60 FPS
python main.py --godmode          # Can't die
```

**Controls:** WASD to move, IJKL to shoot, Enter to restart, Escape to quit.

## Use for RL Training

```python
from robotron import RobotronEnv

env = RobotronEnv(
    headless=True,       # No window (still returns RGB observations)
    fps=0,               # Max speed
    always_move=True,    # Action space: 64 instead of 81
    lives=5,             # More lives = more learning
)

obs, info = env.reset(seed=42)

while True:
    action = env.action_space.sample()  # Your agent here
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated:
        obs, info = env.reset()

env.close()
```

For training, disable visual effects in your config YAML:

```yaml
effects_enabled: false
warp_in_duration: 0
death_duration: 0
level_complete_duration: 0
```

## Key Facts

| | |
|-|-|
| **Action Space** | Discrete(64) with `always_move=True`, Discrete(81) without |
| **Observation** | RGB uint8, 492x665x3 (play area only) |
| **Rewards** | Score delta / 100, death = -1.0, family = 10-50 |
| **Headless FPS** | ~500-1000 on modern hardware |
| **Deterministic** | Yes, via `env.reset(seed=N)` |

## More Info

- **README.md** — Full docs, RL integration examples, config reference
- **examples/** — Runnable code samples
- **robotron/engine/config.yaml** — All configurable game parameters
