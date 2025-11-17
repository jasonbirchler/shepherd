# Push2Controller Tests

This directory contains unit tests for the Shepherd Push2Controller Python application.

## Test Structure

- `test_app.py` - Tests for main application class and mode management
- `test_settings_mode.py` - Tests for settings mode functionality including Pages enum
- `test_main_controls_mode.py` - Tests for transport controls and main interface
- `test_definitions.py` - Tests for constants, colors, and base classes
- `test_utils.py` - Tests for utility functions and display helpers
- `conftest.py` - Pytest fixtures and configuration
- `run_tests.py` - Standalone test runner script

## Running Tests

### Using pytest (recommended)
```bash
cd Push2Controller
pip install -r tests/test_requirements.txt
pytest
```

### Using unittest
```bash
cd Push2Controller
python tests/run_tests.py
```

### With coverage
```bash
cd Push2Controller
pytest --cov=. --cov-report=html
```

## Test Features

- **Mocked Dependencies**: All external dependencies (MIDI, Push2 hardware, etc.) are mocked
- **Isolated Tests**: Each test runs independently with fresh fixtures
- **Comprehensive Coverage**: Tests cover core functionality, mode management, and UI components
- **Easy Extension**: Add new test files following the `test_*.py` pattern

## Key Test Areas

1. **Mode Management**: Testing activation/deactivation of different controller modes
2. **Button Handling**: Testing Push2 button press/release logic
3. **Settings Management**: Testing the new enum-based page system
4. **Transport Controls**: Testing play/stop/record functionality
5. **Color System**: Testing the dynamic color generation system
6. **Utility Functions**: Testing display and text rendering helpers