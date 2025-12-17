# Contributing to Faster APP

Thank you for your interest in contributing to Faster APP! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mautops/faster-app.git
   cd faster-app
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync --all-extras --dev
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## Code Quality Standards

### Linting and Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check code style
uv run ruff check faster_app/

# Auto-fix issues
uv run ruff check --fix faster_app/

# Format code
uv run ruff format faster_app/
```

### Type Checking

We use [mypy](https://mypy-lang.org/) for static type checking:

```bash
uv run mypy faster_app/
```

### Testing

Run tests with pytest:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=faster_app --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py -v
```

## Coding Guidelines

### Python Style

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use double quotes for strings
- Add docstrings to all public classes and functions

### Docstring Format

Use Google-style docstrings:

```python
def example_function(arg1: str, arg2: int) -> bool:
    """
    Brief description of the function.
    
    Detailed description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg2 is negative
        
    Example:
        >>> example_function("test", 5)
        True
    """
    pass
```

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(models): add SoftDeleteModel base class

Adds a new base model class that implements soft delete
functionality with a deleted_at timestamp field.

Closes #123
```

## Pull Request Process

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   uv run ruff check --fix faster_app/
   uv run ruff format faster_app/
   uv run mypy faster_app/
   uv run pytest
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request:**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI checks pass

## Project Structure

```
faster_app/
├── apps/           # Demo applications
├── commands/       # CLI command implementations
├── middleware/     # Middleware components
├── models/         # Model base classes
├── routes/         # Route definitions
├── settings/       # Configuration management
└── utils/          # Utility functions
```

## Getting Help

- 📚 [Documentation](https://mautops.github.io/faster-app/)
- 💬 [Discussions](https://github.com/mautops/faster-app/discussions)
- 🐛 [Issues](https://github.com/mautops/faster-app/issues)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## License

By contributing to Faster APP, you agree that your contributions will be licensed under the MIT License.
