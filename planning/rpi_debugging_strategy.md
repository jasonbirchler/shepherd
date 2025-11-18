# RPi Transport Controls and MIDI Debugging Strategy

## Priority 1: Add Targeted Logging Points

### 1.1 Build Configuration Verification
Add logging at application startup to verify build configuration:

**Location**: `Sequencer::Sequencer()` (around line 40)
```cpp
DBG("=== BUILD CONFIGURATION ===");
DBG("RPI_BUILD defined: " << #ifdef RPI_BUILD << "YES" << #else << "NO" << #endif);
DBG("Current platform: Linux");
DBG("JUCE Audio Devices: " << juce::AudioDeviceManager::getInstance()->getCurrentAudioDevice()->getName() << " (" << juce::AudioDeviceManager::getInstance()->getCurrentAudioDevice()->getTypeName() << ")");
```

### 1.2 MIDI Device Initialization Logging
Enhanced logging in MIDI initialization methods:

**Location**: `Sequencer::initializeMIDIInputs()` (around line 421)
```cpp
std::cout << "=== MIDI INPUT INITIALIZATION ===" << std::endl;
auto availableInputs = juce::MidiInput::getAvailableDevices();
std::cout << "Available MIDI inputs:" << std::endl;
for (const auto& device : availableInputs) {
    std::cout << "- " << device.name << " (ID: " << device.identifier << ")" << std::endl;
}
```

**Location**: `Sequencer::initializeMIDIOutputs()` (around line 475)
```cpp
std::cout << "=== MIDI OUTPUT INITIALIZATION ===" << std::endl;
auto availableOutputs = juce::MidiOutput::getAvailableDevices();
std::cout << "Available MIDI outputs:" << std::endl;
for (const auto& device : availableOutputs) {
    std::cout << "- " << device.name << " (ID: " << device.identifier << ")" << std::endl;
}
```

### 1.3 Hardware Device State Logging
**Location**: `Sequencer::initializeHardwareDevices()` (around line 745)
```cpp
std::cout << "=== HARDWARE DEVICES INITIALIZATION ===" << std::endl;
std::cout << "Hardware devices configuration:" << std::endl;
for (auto hwDevice : hardwareDevices->objects) {
    std::cout << "- " << hwDevice->getName() << " (" << hwDevice->getType() << ")" << std::endl;
    std::cout << "  MIDI Device Name: " << hwDevice->getMidiOutputDeviceName() << std::endl;
    std::cout << "  MIDI Channel: " << hwDevice->getMidiOutputChannel() << std::endl;
    std::cout << "  MIDI Initialized: " << (hwDevice->isMidiInitialized() ? "YES" : "NO") << std::endl;
}
```

### 1.4 Transport Control Logging
**Location**: `Sequencer::processMessageFromController()` (ACTION_ADDRESS_TRANSPORT_PLAY_STOP)
```cpp
DBG("=== TRANSPORT CONTROL RECEIVED ===");
DBG("Action: " << action);
DBG("Current playing state: " << musicalContext->playheadIsPlaying());
DBG("shouldToggleIsPlaying set to: true");
```

### 1.5 MIDI Message Flow Logging
**Location**: `Track::writeLastSliceMidiBufferToHardwareDeviceMidiBuffer()` (around line 348)
```cpp
DBG("=== MIDI OUTPUT ===");
DBG("Track: " << getName());
DBG("Output device: " << getMidiOutputDeviceName());
DBG("Channel: " << getMidiOutputChannel());
DBG("MIDI buffer events: " << lastSliceMidiBuffer.getNumEvents());

if (hardwareDeviceMidiBuffer != nullptr) {
    DBG("Hardware device buffer events: " << hardwareDeviceMidiBuffer->getNumEvents());
} else {
    DBG("WARNING: Hardware device MIDI buffer is nullptr!");
}
```

## Priority 2: System Diagnostics

### 2.1 ALSA Device Availability Check
Create a system check for ALSA MIDI devices:

**Add to**: `Sequencer::initializeMIDIInputs()`
```cpp
// Test ALSA availability
FILE* pipe = popen("aconnect -l", "r");
if (pipe) {
    char buffer[256];
    std::cout << "=== ALSA CONNECTIONS ===" << std::endl;
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        std::cout << buffer;
    }
    pclose(pipe);
} else {
    std::cout << "ALSA connection check failed" << std::endl;
}
```

### 2.2 Memory and Performance Monitoring
**Add to**: `Sequencer::timerCallback()` (around line 1115)
```cpp
// Add periodic system status logging (every 30 seconds)
static int lastStatusTime = 0;
if (juce::Time::getMillisecondCounter() - lastStatusTime > 30000) {
    lastStatusTime = juce::Time::getMillisecondCounter();
    
    DBG("=== SYSTEM STATUS (30s) ===");
    DBG("Playing: " << musicalContext->playheadIsPlaying());
    DBG("MIDI Input Devices: " << midiInDevices.size());
    DBG("MIDI Output Devices: " << midiOutDevices.size());
    DBG("Tracks: " << tracks->objects.size());
    
    // Check for any failed device initializations
    for (auto hwDevice : hardwareDevices->objects) {
        if (!hwDevice->isMidiInitialized()) {
            DBG("WARNING: Hardware device not MIDI initialized: " << hwDevice->getName());
        }
    }
}
```

## Priority 3: Connection Testing

### 3.1 Hardware Device Connection Test
**Add to**: `HardwareDevice::sendMidi()` (around line 51 in HardwareDevice.h)
```cpp
void HardwareDevice::sendMidi(juce::MidiMessage msg) {
    if (!isMidiInitialized()) {
        DBG("WARNING: Attempting to send MIDI to uninitialized device: " << getName());
        return;
    }
    
    DBG("Sending MIDI to " << getName() << " (ch " << getMidiOutputChannel() << "): " 
        << (int)msg.getData()[0] << " " << (int)msg.getData()[1] << " " << (int)msg.getData()[2]);
    
    auto deviceData = getMidiOutputDeviceData(getMidiOutputDeviceName());
    if (deviceData && deviceData->device) {
        deviceData->device->sendMessageNow(msg);
    } else {
        DBG("ERROR: MIDI device data or device is null for " << getName());
    }
}
```

## Priority 4: Timeout and Retry Logic

### 4.1 MIDI Initialization Timeout Handling
**Modify**: `Sequencer::timerCallback()` to include more aggressive retry logic
```cpp
// More frequent retry attempts for MIDI initialization on RPi
if (shouldTryInitializeMidiOutputs) {
    if (juce::Time::getMillisecondCounter() - lastTimeMidiOutputInitializationAttempted > 5000) {
        DBG("MIDI output initialization retry after 5s timeout");
        initializeMIDIOutputs();
    }
}
```

## Testing Protocol

### Step 1: Run with enhanced logging
1. Apply all logging changes
2. Rebuild on RPi: `make clean && make CONFIG=Debug`
3. Run application and observe console output
4. Test transport controls and note triggering
5. Capture full output for analysis

### Step 2: Verify RPI_BUILD flag
1. Check if RPI_BUILD appears in build configuration logs
2. If missing, apply fix and retest

### Step 3: Verify MIDI device enumeration
1. Check available MIDI devices list
2. Verify hardware device initialization status
3. Test ALSA connectivity

### Step 4: Monitor real-time performance
1. Watch system status logs
2. Check for MIDI message flow
3. Verify transport state changes

## Expected Outcomes

**If RPI_BUILD is missing**: Transport controls will work after adding compilation flag
**If MIDI initialization fails**: Enhanced logging will reveal specific device issues
**If timing problems**: Real-time performance monitoring will show bottlenecks
**If WebSocket issues**: Transport control logging will show if messages reach the backend
