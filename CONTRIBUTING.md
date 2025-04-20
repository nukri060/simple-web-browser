# Contributing to RivaBrowser

Thank you for your interest in contributing to RivaBrowser! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Requests](#pull-requests)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/simple-web-browser.git
   cd simple-web-browser
   ```
3. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   pip install -r requirements-dev.txt
   ```

## Development Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes following the code style guidelines

3. Write or update tests for your changes

4. Update documentation as needed

5. Commit your changes using Conventional Commits:
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in feature"
   git commit -m "docs: update documentation"
   ```

6. Push your changes:
   ```bash
   git push origin your-branch-name
   ```

7. Create a Pull Request

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all new code
- Keep functions small and focused (preferably under 50 lines)
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Use Google-style docstrings:
  ```python
  def function_name(arg1: str, arg2: int) -> bool:
      """Short description of the function.

      Args:
          arg1: Description of first argument.
          arg2: Description of second argument.

      Returns:
          Description of return value.

      Raises:
          ExceptionType: Description of when this exception is raised.
      """
  ```

## Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a PR
- Use pytest for testing
- Follow the existing test structure
- Aim for high test coverage
- Run tests locally:
  ```bash
  pytest
  pytest --cov=riva  # With coverage
  ```

## Documentation

- Update relevant documentation for all changes
- Follow the existing documentation style
- Include examples for new features
- Update CHANGELOG.md for significant changes
- Keep docstrings up to date

## Pull Requests

1. Ensure your PR description clearly explains:
   - What changes were made
   - Why they were made
   - How they were tested
   - Any breaking changes

2. Reference any related issues

3. Ensure all CI checks pass

4. Request review from maintainers

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create a release tag
4. Build and publish to PyPI

## Questions?

Feel free to open an issue for any questions about contributing to RivaBrowser.
