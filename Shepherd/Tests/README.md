# Shepherd Backend Testing

This directory contains tests for the Shepherd backend application.

## Current Status

✅ **Basic Testing Framework** - Implemented and working
- Simple C++ test framework without JUCE dependencies
- Basic tests for core logic validation
- Makefile-based build system

## Test Structure

### 1. Simple Tests (`simple_test.cpp`)
- **Purpose**: Test core logic without JUCE dependencies
- **Coverage**: Basic math operations, MIDI validation, string utilities
- **Run**: `make -f simple_makefile test`

### 2. Backend Component Tests (`backend_component_tests.cpp`)
- **Purpose**: Test core backend components using mocks
- **Coverage**: MusicalContext, Track, Session coordination, Hardware device management
- **Run**: `make -f backend_component_makefile test`
- **Status**: ✅ 6 comprehensive component tests

### 3. JUCE-like Tests (`minimal_juce_test.cpp`)
- **Purpose**: Demonstrate JUCE-style testing concepts
- **Coverage**: ValueTree-like operations, String handling
- **Run**: `make -f minimal_juce_makefile test`
- **Status**: ✅ Working proof of concept

### 4. JUCE-based Tests (Future)
- **Purpose**: Test actual JUCE-dependent components
- **Coverage**: Real MusicalContext, HardwareDevice, ValueTree operations
- **Status**: Complex due to JUCE build dependencies

## Running Tests

```bash
# Run simple tests (no dependencies)
cd Shepherd/Tests
make -f simple_makefile test

# Run mock framework tests
make -f mock_makefile test

# Run integration tests (using mocks)
make -f integration_makefile test

# Run backend component tests (using mocks)
make -f backend_component_makefile test

# Run minimal JUCE-like tests
make -f minimal_juce_makefile test

# Run all tests at once
bash run_all_tests.sh

# Clean up
make -f simple_makefile clean
make -f mock_makefile clean
make -f integration_makefile clean
make -f backend_component_makefile clean
make -f minimal_juce_makefile clean
```

## Test Categories

### ✅ Implemented
1. **Basic Math Operations**
   - BPM to sample rate conversions
   - Timing calculations

2. **MIDI Validation**
   - Channel range validation (1-16)
   - Basic MIDI message validation

3. **String Utilities**
   - Device name truncation
   - Short name generation

### 🚧 Planned (Next Phase)
1. **MusicalContext Tests**
   - BPM/meter setting and getting
   - Playhead position management
   - Metronome functionality
   - Bar counting logic

2. **HardwareDevice Tests**
   - Device creation and configuration
   - MIDI channel management
   - Device type validation
   - UUID handling

3. **Integration Tests**
   - ✅ MIDI message flow (with mocks)
   - ✅ State synchronization (with mocks)
   - ✅ WebSocket communication (with mocks)

### ✅ Mock Framework (Implemented)
1. **Mock MIDI Devices**
   - MockMidiDeviceManager for device management
   - MockMidiMessage for MIDI data
   - Message tracking and validation

2. **Mock WebSocket Connections**
   - MockWebSocketConnection for backend communication
   - Message sending/receiving simulation
   - Handler registration and testing

3. **Mock Timing System**
   - MockTimer for deterministic timing tests
   - MockGlobalSettings for configuration
   - Controllable time advancement

### 🔮 Future Phases
1. **Performance Tests**
   - Real-time processing validation
   - Memory usage monitoring
   - Latency measurement

## Testing Strategy

### Phase 1: Foundation (Current)
- ✅ Basic test framework
- ✅ Core logic validation
- ✅ Build system setup

### Phase 2: Core Components
- JUCE integration for ValueTree testing
- MusicalContext comprehensive tests
- HardwareDevice functionality tests

### Phase 3: Integration
- End-to-end MIDI flow testing
- WebSocket message handling
- State management validation

### Phase 4: Advanced
- Performance benchmarking
- Memory leak detection
- Real-time constraint validation

## Benefits of Starting with Backend Tests

1. **Foundation First**: Backend is the core of the system
2. **Isolated Testing**: Fewer dependencies than frontend
3. **Clear Interfaces**: Well-defined classes and methods
4. **Critical Path**: Backend bugs affect entire system
5. **Performance Critical**: Real-time constraints need validation

## Next Steps

1. **Integrate with JUCE Build System**
   - Modify existing Xcode/Makefile to include tests
   - Resolve JUCE header dependencies

2. **Expand Test Coverage**
   - Add MusicalContext tests
   - Add HardwareDevice tests
   - Add ValueTree operation tests

3. **Add Mock Framework**
   - Mock MIDI devices for testing
   - Mock WebSocket connections
   - Simulated timing for deterministic tests

4. **Continuous Integration**
   - Automated test running
   - Test coverage reporting
   - Performance regression detection

## File Structure

```
Tests/
├── README.md                 # This file
├── simple_test.cpp          # Basic tests (no JUCE)
├── simple_makefile          # Build for simple tests
├── mocks.h                  # Mock framework header
├── mock_tests.cpp           # Mock framework tests
├── mock_makefile            # Build for mock tests
├── integration_example.cpp  # Integration test examples
├── integration_makefile     # Build for integration tests
├── test_main.cpp            # JUCE-based test main (future)
├── test_musical_context.cpp # MusicalContext tests (future)
├── test_hardware_device.cpp # HardwareDevice tests (future)
├── Makefile                 # JUCE-based build (future)
└── CMakeLists.txt           # CMake config (future)
```

This testing foundation provides a solid base for expanding test coverage as the project grows.