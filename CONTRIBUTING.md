# Contributing Guidelines

Thank you for considering contributing to the SharePoint MCP project. Please follow these guidelines when contributing to the project.

## Setting Up Development Environment

1. Fork and clone the repository.

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Coding Standards

- Follow the [PEP 8](https://peps.python.org/pep-0008/) coding style
- Include docstrings for all functions, classes, and modules
- Include tests for your code changes
- Run linting and formatting before committing:

```bash
# Format code
black src tests

# Run linter
ruff check src tests
```

## Branch Strategy

- The `main` branch always reflects the latest stable release
- Development is done from the `develop` branch
- Feature development should be done in branches named `feature/your-feature-name`
- Bug fixes should be done in branches named `fix/bug-description`

## Pull Requests

1. Create a development branch from the appropriate branch
2. Make your changes and add necessary tests
3. Ensure all tests pass
4. Update the `CHANGELOG.md`
5. Create a pull request with a detailed description of your changes

## Commit Message Guidelines

Commit messages should follow this format:

```
type(scope): brief description

detailed description (if needed)
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation-only changes
- `style`: Changes that don't affect the meaning of the code (whitespace, formatting, etc.)
- `refactor`: Code changes that neither fix a bug nor add a feature
- `test`: Adding or correcting tests
- `chore`: Changes to the build process or auxiliary tools

## Testing

Make sure to add tests for any new features or bug fixes. Tests should be placed in the `tests` directory.

```bash
# Run tests
pytest
```

## Documentation

- Update documentation related to your code changes
- Add documentation for new features

## Questions

If you have questions or concerns, please open an issue with the "question" tag.