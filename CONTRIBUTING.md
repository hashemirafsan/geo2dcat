# Contributing to geo2dcat

Thank you for your interest in contributing to geo2dcat! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to be respectful and professional in all interactions.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/hashemirafsan/geo2dcat/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce (if applicable)
   - Expected vs actual behavior
   - System information (Python version, OS)
   - Sample files (if possible)

### Suggesting Features

1. Open a [Discussion](https://github.com/hashemirafsan/geo2dcat/discussions) first
2. Describe the use case and benefits
3. Consider implementation complexity
4. Get feedback before starting work

### Contributing Code

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/hashemirafsan/geo2dcat.git
cd geo2dcat

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[all,dev]"

# Or use Docker
docker compose build geo2dcat
make shell
```

#### Development Workflow

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. Make your changes:
   - Write clean, documented code
   - Follow existing code style
   - Add type hints where possible
   - Update documentation if needed

4. Add tests:
   ```bash
   # Run tests
   pytest tests/test_your_feature.py -v
   
   # Check coverage
   pytest --cov=geo2dcat --cov-report=html
   ```

5. Lint your code:
   ```bash
   # Format code
   ruff format geo2dcat tests
   
   # Check linting
   ruff check geo2dcat tests
   
   # Type checking
   mypy geo2dcat
   ```

6. Commit your changes:
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

7. Push and create PR:
   ```bash
   git push origin feature/amazing-feature
   ```

### Code Style Guidelines

- Follow PEP 8
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public functions/classes
- Type hints are encouraged

Example:
```python
from typing import Optional, Dict, Any

def extract_metadata(filepath: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract metadata from geospatial file.
    
    Args:
        filepath: Path to the input file
        options: Optional extraction options
        
    Returns:
        Dictionary containing normalized metadata
        
    Raises:
        FileNotFoundError: If filepath doesn't exist
        ValueError: If format is unsupported
    """
    # Implementation here
    pass
```

### Adding New Format Support

To add support for a new file format:

1. Create extractor module:
   ```bash
   touch geo2dcat/extractors/myformat.py
   ```

2. Implement the extractor:
   ```python
   from geo2dcat.types import NormalizedMetadata, VariableInfo
   
   def extract_myformat(filepath: str) -> NormalizedMetadata:
       """Extract metadata from MyFormat files."""
       # Your implementation
       return {
           "format": "MyFormat",
           "title": ...,
           # All required fields
       }
   ```

3. Register in `geo2dcat/extractors/__init__.py`:
   ```python
   EXTRACTORS["myformat"] = extract_myformat
   SUPPORTED_EXTENSIONS[".myf"] = "myformat"
   ```

4. Add tests in `tests/test_myformat.py`

5. Update documentation

### Adding New CF Mappings

1. Edit `geo2dcat/mappings/cf_standard_names.py`:
   ```python
   CF_STANDARD_NAME_MAPPING.update({
       "new_variable": "sweet:NewConcept",
       # Add more mappings
   })
   ```

2. Add theme mapping in `geo2dcat/mappings/themes.py`:
   ```python
   THEME_MAPPING["sweet:NewConcept"] = "theme:RelevantTheme"
   ```

3. Add tests to verify mappings work correctly

### Testing Guidelines

- Write tests for all new functionality
- Use pytest fixtures for common test data
- Test both success and error cases
- Mock external dependencies
- Aim for >80% test coverage

Example test:
```python
import pytest
from geo2dcat import convert

def test_convert_valid_file(tmp_path):
    """Test converting a valid file."""
    # Create test file
    test_file = tmp_path / "test.nc"
    # ... create file content
    
    # Test conversion
    result = convert(str(test_file))
    
    # Assertions
    assert result["@type"] == "dcat:Dataset"
    assert result["dct:format"] == "NetCDF"
    assert "cf:variableMappings" in result
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new code
- Update examples if API changes
- Add to CHANGELOG.md

### Pull Request Guidelines

Your PR should:
- Have a clear title and description
- Reference any related issues
- Pass all CI checks
- Include tests for new features
- Update documentation as needed
- Be based on the latest main branch

PR title format:
- `feat: Add support for Zarr format`
- `fix: Handle missing CRS in GeoTIFF files`
- `docs: Improve installation instructions`
- `test: Add coverage for edge cases`

## Getting Help

- Check existing [documentation](README.md)
- Search [closed issues](https://github.com/hashemirafsan/geo2dcat/issues?q=is%3Aclosed)
- Ask in [Discussions](https://github.com/hashemirafsan/geo2dcat/discussions)
- Check the [Wiki](https://github.com/hashemirafsan/geo2dcat/wiki)

## Release Process

Maintainers will:
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. Build and publish to PyPI
5. Create GitHub release

## Recognition

Contributors will be:
- Listed in the [Contributors](https://github.com/hashemirafsan/geo2dcat/graphs/contributors) page
- Mentioned in release notes
- Added to CONTRIBUTORS.md (for significant contributions)

Thank you for helping make geo2dcat better!