# Contributing to Robotron 2084 Gymnasium Environment

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- [Poetry](https://python-poetry.org/) for dependency management

### Getting Started

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/robotron-2084.git
   cd robotron-2084
   ```

2. **Install dependencies:**
   ```bash
   poetry install --with dev,examples
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Or using poetry directly
poetry run pytest
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check
```

### Before Committing

Run the full quality check:

```bash
make format lint type-check test
```

## Code Style

- **Formatting:** We use [Black](https://black.readthedocs.io/) with 100 character line length
- **Linting:** We use [Ruff](https://docs.astral.sh/ruff/) for fast Python linting
- **Type Hints:** Add type hints to all public APIs
- **Docstrings:** Use Google-style docstrings for all public functions and classes

### Example

```python
def my_function(arg1: int, arg2: str) -> bool:
    """
    Brief description of function.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

## Adding Features

### Adding a New Enemy Type

1. Create a new file in `robotron/engine/entities/`
2. Inherit from `Base` class
3. Implement required methods:
   - `get_animations()`: Return sprite animations
   - `update()`: Game logic for each frame
4. Use seeded random helpers:
   - `self.random_int(low, high)` instead of `random.randint()`
   - `self.random_float(low, high)` instead of `random.random()`
   - `self.random_choice(seq)` instead of `random.choice()`
5. Add configuration to `robotron/engine/config.yaml`
6. Import and spawn in `Engine._initialize_level()`
7. Add tests in `tests/`

### Adding Examples

Add example scripts to `examples/` with:
- Clear docstring explaining what it demonstrates
- Complete, runnable code
- Comments explaining key points
- Update `examples/README.md`

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use pytest fixtures for common setups
- Test both normal and edge cases
- Include tests for reproducibility (seeding)

Example test:

```python
def test_environment_reset():
    """Test that environment resets correctly."""
    env = RobotronEnv(headless=True)
    obs, info = env.reset(seed=42)

    assert obs.shape == env.observation_space.shape
    assert info['score'] == 0
    assert info['lives'] == 3

    env.close()
```

## Documentation

### Updating Documentation

When adding features, update:
- `README.md` - User-facing documentation
- `CLAUDE.md` - Developer/architecture documentation
- Docstrings in code
- Examples if applicable

### Documentation Style

- Use clear, concise language
- Include code examples
- Keep formatting consistent
- Test all code examples

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clear, focused commits
   - Add tests for new features
   - Update documentation

3. **Run quality checks:**
   ```bash
   make format lint type-check test
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub

5. **PR Requirements:**
   - Clear description of changes
   - All tests passing
   - Code formatted and linted
   - Documentation updated
   - No merge conflicts

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues and PRs first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
