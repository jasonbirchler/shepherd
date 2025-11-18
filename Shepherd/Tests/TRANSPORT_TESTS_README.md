# MIDI Transport Message Separation Tests

This document describes the comprehensive test suite for the MIDI transport message separation feature implemented in Shepherd.

## Overview

The transport separation feature allows independent routing of:
- **MIDI Clock Messages** (24 PPQ timing) → `midiDevicesToSendClockTo`
- **MIDI Transport Messages** (start/stop/continue) → `midiDevicesToSendTransportTo`

## Test Files

### 1. `midi_transport_tests.cpp`
**Purpose**: Tests the core MIDI transport separation logic

**Test Cases**:
- **Clock Only Device**: Verifies devices receive only clock messages when configured for clock only
- **Both Messages Device**: Tests devices that receive both clock and transport messages
- **Multiple Devices**: Validates routing to multiple devices with different configurations
- **Continue Command**: Tests start/stop/continue transport message sequence
- **Empty Device Lists**: Ensures no messages sent when no devices configured
- **Nonexistent Devices**: Handles gracefully when configured devices don't exist
- **Clock Timing Accuracy**: Verifies exact 24 PPQ clock message generation

**Build**: `make -f Makefile_transport test`

### 2. `transport_config_tests.cpp`
**Purpose**: Tests configuration file parsing for transport separation

**Test Cases**:
- **Separate Clock and Transport Devices**: Parses different device lists correctly
- **Empty Arrays**: Handles empty device arrays gracefully
- **Missing Transport Config**: Backward compatibility when only clock devices configured
- **Single Device Arrays**: Correctly parses single-device configurations
- **Device Name Overlap**: Allows same device in both clock and transport lists
- **Special Characters**: Handles device names with dashes, underscores, parentheses, spaces

**Build**: `make -f Makefile_config test`

### 3. `backend_component_tests.cpp` (Enhanced)
**Purpose**: Tests backend components with mock framework

**Existing Test Cases**:
- Musical context (BPM, timing, meter, metronome)
- Track hardware device assignment
- MIDI message routing
- Multi-track coordination
- Hardware device channel management

**Build**: `make backend_component_tests`

## Configuration Format

```json
{
    "midiDevicesToSendClockTo": ["Device1", "Device2"],
    "midiDevicesToSendTransportTo": ["Device1", "Device3"],
    "pushClockDeviceName": "Ableton Push 2 Live Port"
}
```

## Test Results

All transport-related tests pass:
- **MIDI Transport Tests**: 7/7 passed
- **Transport Config Tests**: 6/6 passed  
- **Backend Component Tests**: 6/6 passed

## Integration with CI/CD

Tests are integrated into:
- **Local Development**: `run_all_tests.sh` includes transport tests
- **GitHub Actions**: Automatically run when backend files change
- **Build System**: Makefile targets for individual test suites

## Mock Framework

The tests use a comprehensive mock framework (`mocks.h`) that provides:
- `MockMidiDeviceManager`: Simulates MIDI device management
- `MockSequencer`: Simulates transport message generation
- `MockBackendSettings`: Simulates configuration parsing
- `MockTimer`: Deterministic timing for tests

## Key Features Tested

1. **Message Separation**: Clock and transport messages route independently
2. **Device Overlap**: Same device can receive both message types
3. **Configuration Parsing**: JSON parsing with error handling
4. **Backward Compatibility**: Works when transport config missing
5. **Edge Cases**: Empty configs, nonexistent devices, special characters
6. **Timing Accuracy**: Precise 24 PPQ clock generation
7. **Transport Commands**: Start, stop, continue message handling

## Running Tests

```bash
# Individual test suites
make -f Makefile_transport test
make -f Makefile_config test

# All transport tests
make midi_transport_tests transport_config_tests
./midi_transport_tests && ./transport_config_tests

# All backend tests
bash run_all_tests.sh
```

## Future Enhancements

Potential areas for additional testing:
- Real-time performance under load
- MIDI device connection/disconnection handling
- Configuration hot-reloading
- Push2 clock burst timing validation
- Network latency impact on transport sync