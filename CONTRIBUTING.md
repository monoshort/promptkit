# Contributing to promptkit

Thank you for your interest in contributing to promptkit!

## Development Setup

```bash
git clone https://github.com/monoshort/promptkit.git
cd promptkit
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]
```

## Running Tests

```bash
pytest
```

## Code Quality

```bash
ruff check .
ruff format .
```

## Pull Request Process

1. Fork the repo and create your feature branch from `main`.
2. Make your changes with tests.
3. Ensure tests pass and code is formatted.
4. Open a PR with a clear description of the change and motivation.
5. Be kind and constructive in discussions.

## What We're Looking For

- Guardrail improvements and new safety patterns
- Better support for different LLM providers
- Documentation and example projects
- Performance or DX improvements
- Real usage stories (blog posts, etc.)

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/). By participating you agree to uphold it. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions?

Open an issue or start a discussion. We're happy to help new contributors.
