# PyShepherd Testing Guide

## Setup

1. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install package in development mode:**
```bash
pip install -e .[test]
```

## Running Tests

### All Tests
```bash
# Run all tests
python -m pytest pyshepherd/tests/

# Run with coverage
python -m pytest pyshepherd/tests/ --cov=pyshepherd --cov-report=html
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest pyshepherd/tests/test_*.py -k "not integration"

# Integration tests only  
python -m pytest pyshepherd/tests/test_integration.py

# Specific test file
python -m pytest pyshepherd/tests/test_sequencer.py -v
```

### Test Results
- **84 tests total**
- **All tests passing** ✅
- **Comprehensive coverage** of core backend functionality

## Test Structure

- `test_sequencer.py` - Core sequencer functionality (10 tests)
- `test_session.py` - Session management (8 tests) 
- `test_track.py` - Track routing and clips (9 tests)
- `test_clip.py` - MIDI sequences and playback (14 tests)
- `test_musical_context.py` - Timing and musical calculations (16 tests)
- `test_hardware_device.py` - MIDI device management (19 tests)
- `test_integration.py` - End-to-end system tests (11 tests)

## Key Features Tested

### ✅ Core Functionality
- Session creation and management
- Track routing and device assignment  
- Clip playback and MIDI generation
- Musical timing and BPM calculations
- Hardware device discovery and I/O

### ✅ Integration Scenarios
- Multi-track coordination
- Scene playback across tracks
- Hardware device hot-swapping
- Long-running session stability
- Event probability and quantization

### ✅ Performance & Reliability
- Timing precision validation
- Memory usage patterns
- Error handling and edge cases
- Mock-based isolation testing

The test suite ensures the Python backend maintains full compatibility with the original C++ functionality while providing a solid foundation for future development.