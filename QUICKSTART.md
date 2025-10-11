# Robotron 2084 - Quick Start Guide

## 🚀 Installation (60 seconds)

```bash
# Using Poetry (recommended)
poetry install && poetry shell

# Using pip
pip install -r requirements.txt
```

## 🎮 Run the Game

```bash
# Human playable (keyboard: WASD + IJKL)
python main.py

# Or with Poetry
poetry run python main.py
```

## 🤖 Use in Your RL Code

```python
from robotron import RobotronEnv

# Create environment
env = RobotronEnv(
    fps=0,           # Max speed
    headless=True,   # Off-screen rendering (fast + visual observations!)
    always_move=True # Smaller action space (64 vs 81)
)

# Standard Gymnasium API
obs, info = env.reset(seed=42)

while True:
    action = your_agent.predict(obs)
    obs, reward, done, truncated, info = env.step(action)
    if done:
        break

env.close()
```

## 📊 Key Info

| Feature | Value |
|---------|-------|
| Action Space | Discrete(81) or Discrete(64) |
| Observation | RGB (492×665×3) |
| FPS (headless) | ~500-1000 |
| Python | 3.10, 3.11, 3.12 |
| Seeded | ✅ Fully deterministic |

## 🔧 Common Commands

```bash
# Run tests
make test

# Format code
make format

# Run examples
make examples

# Clean up
make clean
```

## 📖 More Info

- **README.md** - Full documentation
- **examples/** - Code samples
- **CLAUDE.md** - Architecture overview
- **CONTRIBUTING.md** - Development guide

## 💡 Pro Tips

1. **Always use seeding** for reproducible experiments: `env.reset(seed=42)`
2. **Use headless mode** for training: off-screen rendering gives you speed + visual observations
3. **Check examples/** for common patterns
4. **Read info dict** for game state: `info['score']`, `info['lives']`, etc.

## 🐛 Troubleshooting

**Import error?**
```bash
poetry install  # or pip install -r requirements.txt
```

**Too slow?**
```python
env = RobotronEnv(fps=0, headless=True)  # Max speed!
```

**Not deterministic?**
```python
env.reset(seed=42)  # Always seed!
```

---

**Ready to train?** Check out `examples/basic_usage.py` to get started!
