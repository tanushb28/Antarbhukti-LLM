# Testing Documentation

This directory contains comprehensive unit tests for the Antarbhukti-LLM project.

## Test Structure

```
tests/
├── __init__.py
├── README.md
├── test_data/
│   ├── simple_sfc.txt       # Simple SFC for testing
│   ├── modified_sfc.txt     # Modified SFC for comparison tests
│   └── invalid_sfc.txt      # Invalid SFC for error testing
├── test_sfc.py             # Tests for SFC module
├── test_verifier.py        # Tests for Verifier module
├── test_genreport.py       # Tests for GenReport module
└── test_llm_manager.py     # Tests for LLM_Mgr module
```

## Running Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Running Specific Test Files

```bash
# Run SFC tests only
pytest tests/test_sfc.py -v

# Run Verifier tests only
pytest tests/test_verifier.py -v

# Run GenReport tests only
pytest tests/test_genreport.py -v

# Run LLM Manager tests only
pytest tests/test_llm_manager.py -v
```

### Running Tests by Category

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Test Coverage

The tests aim for 80% coverage minimum. You can check coverage with:

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in your browser
```

## Test Data

The `test_data/` directory contains:

- `simple_sfc.txt`: A basic SFC with 3 steps and 2 transitions
- `modified_sfc.txt`: A modified version for comparison testing
- `invalid_sfc.txt`: An invalid SFC for testing error handling

## Test Modules

### test_sfc.py
Tests the SFC (Sequential Function Chart) module:
- File loading and parsing
- Data validation
- Type checking
- Error handling
- Export functionality

### test_verifier.py
Tests the Verifier module:
- Petri net conversion
- Containment checking
- Path analysis
- Z3 integration (mocked)
- Cut point detection

### test_genreport.py
Tests the GenReport module:
- DOT file generation
- PNG conversion (mocked)
- HTML report generation
- File I/O operations

### test_llm_manager.py
Tests the LLM_Mgr module:
- Configuration validation
- API integration (mocked)
- Code extraction
- Error handling

## Mocking

External dependencies are mocked in tests:
- Azure OpenAI API calls
- Graphviz subprocess calls
- File system operations where appropriate
- Z3 solver operations

## Continuous Integration

Tests are automatically run on GitHub Actions for:
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Code linting with flake8
- Security scanning with bandit and safety
- Type checking with mypy
- Code formatting with black

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Include docstrings for test methods
3. Use appropriate fixtures and mocking
4. Ensure tests are independent and isolated
5. Add test data files to `test_data/` if needed 