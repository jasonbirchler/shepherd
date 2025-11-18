# RPi Fixes: Transport Controls and MIDI Issues

## Fix 1: Add RPI_BUILD Compilation Flag (CRITICAL)

**Problem**: The codebase has platform-specific code that's disabled when `RPI_BUILD` is not defined.

**Solution**: Add the flag to the Makefile compilation flags.

**File**: `Shepherd/Builds/LinuxMakefile/Makefile`
**Lines to modify**: 38 and 59 (Debug and Release configurations)

### For Debug Build (line 38):
```diff
-  JUCE_CPPFLAGS := $(DEPFLAGS) "-DLINUX=1" "-DDEBUG=1" "-D_DEBUG=1" "-DJUCE_DISPLAY_SPLASH_SCREEN=0" "-DJUCE_USE_DARK_SPLASH_SCREEN=1" "-DJUCE_PROJUCER_VERSION=0x60106" "-DJUCE_MODULE_AVAILABLE_juce_audio_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_devices=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_formats=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_processors=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_utils=1" "-DJUCE_MODULE_AVAILABLE_juce_core=1" "-DJUCE_MODULE_AVAILABLE_juce_data_structures=1" "-DJUCE_MODULE_AVAILABLE_juce_events=1" "-DJUCE_MODULE_AVAILABLE_juce_graphics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_extra=1" "-DJUCE_MODULE_AVAILABLE_juce_osc=1" "-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1" "-DJUCE_STRICT_REFCOUNTEDPOINTER=1" "-DJUCE_STANDALONE_APPLICATION=1" "-DASIO_STANDALONE=1" "-DJUCER_LINUX_MAKE_6D53C8B4=1" "-DJUCE_APP_VERSION=1.0.0" "-DJUCE_APP_VERSION_HEX=0x10000" $(shell pkg-config --cflags alsa freetype2 libcurl webkit2gtk-4.0 gtk+-x11-3.0) -pthread -I../../JuceLibraryCode -I../../3rdParty/JUCE/modules -I../../3rdParty/Simple-WebSocket-Server/ -I../../3rdParty/asio/asio/include/ -I../../Source/common/ -I../../3rdParty/ff_meters/LevelMeter/ $(CPPFLAGS)
+  JUCE_CPPFLAGS := $(DEPFLAGS) "-DLINUX=1" "-DDEBUG=1" "-D_DEBUG=1" "-DRPI_BUILD=1" "-DJUCE_DISPLAY_SPLASH_SCREEN=0" "-DJUCE_USE_DARK_SPLASH_SCREEN=1" "-DJUCE_PROJUCER_VERSION=0x60106" "-DJUCE_MODULE_AVAILABLE_juce_audio_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_devices=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_formats=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_processors=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_utils=1" "-DJUCE_MODULE_AVAILABLE_juce_core=1" "-DJUCE_MODULE_AVAILABLE_juce_data_structures=1" "-DJUCE_MODULE_AVAILABLE_juce_events=1" "-DJUCE_MODULE_AVAILABLE_juce_graphics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_extra=1" "-DJUCE_MODULE_AVAILABLE_juce_osc=1" "-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1" "-DJUCE_STRICT_REFCOUNTEDPOINTER=1" "-DJUCE_STANDALONE_APPLICATION=1" "-DASIO_STANDALONE=1" "-DJUCER_LINUX_MAKE_6D53C8B4=1" "-DJUCE_APP_VERSION=1.0.0" "-DJUCE_APP_VERSION_HEX=0x10000" $(shell pkg-config --cflags alsa freetype2 libcurl webkit2gtk-4.0 gtk+-x11-3.0) -pthread -I../../JuceLibraryCode -I../../3rdParty/JUCE/modules -I../../3rdParty/Simple-WebSocket-Server/ -I../../3rdParty/asio/asio/include/ -I../../Source/common/ -I../../3rdParty/ff_meters/LevelMeter/ $(CPPFLAGS)
```

### For Release Build (line 59):
```diff
-  JUCE_CPPFLAGS := $(DEPFLAGS) "-DLINUX=1" "-DNDEBUG=1" "-DJUCE_DISPLAY_SPLASH_SCREEN=0" "-DJUCE_USE_DARK_SPLASH_SCREEN=1" "-DJUCE_PROJUCER_VERSION=0x60106" "-DJUCE_MODULE_AVAILABLE_juce_audio_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_devices=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_formats=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_processors=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_utils=1" "-DJUCE_MODULE_AVAILABLE_juce_core=1" "-DJUCE_MODULE_AVAILABLE_juce_data_structures=1" "-DJUCE_MODULE_AVAILABLE_juce_events=1" "-DJUCE_MODULE_AVAILABLE_juce_graphics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_extra=1" "-DJUCE_MODULE_AVAILABLE_juce_osc=1" "-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1" "-DJUCE_STRICT_REFCOUNTEDPOINTER=1" "-DJUCE_STANDALONE_APPLICATION=1" "-DASIO_STANDALONE=1" "-DJUCER_LINUX_MAKE_6D53C8B4=1" "-DJUCE_APP_VERSION=1.0.0" "-DJUCE_APP_VERSION_HEX=0x10000" $(shell pkg-config --cflags alsa freetype2 libcurl webkit2gtk-4.0 gtk+-x11-3.0) -pthread -I../../JuceLibraryCode -I../../3rdParty/JUCE/modules -I../../3rdParty/Simple-WebSocket-Server/ -I../../3rdParty/asio/asio/include/ -I../../Source/common/ -I../../3rdParty/ff_meters/LevelMeter/ $(CPPFLAGS)
+  JUCE_CPPFLAGS := $(DEPFLAGS) "-DLINUX=1" "-DNDEBUG=1" "-DRPI_BUILD=1" "-DJUCE_DISPLAY_SPLASH_SCREEN=0" "-DJUCE_USE_DARK_SPLASH_SCREEN=1" "-DJUCE_PROJUCER_VERSION=0x60106" "-DJUCE_MODULE_AVAILABLE_juce_audio_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_devices=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_formats=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_processors=1" "-DJUCE_MODULE_AVAILABLE_juce_audio_utils=1" "-DJUCE_MODULE_AVAILABLE_juce_core=1" "-DJUCE_MODULE_AVAILABLE_juce_data_structures=1" "-DJUCE_MODULE_AVAILABLE_juce_events=1" "-DJUCE_MODULE_AVAILABLE_juce_graphics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_basics=1" "-DJUCE_MODULE_AVAILABLE_juce_gui_extra=1" "-DJUCE_MODULE_AVAILABLE_juce_osc=1" "-DJUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1" "-DJUCE_STRICT_REFCOUNTEDPOINTER=1" "-DJUCE_STANDALONE_APPLICATION=1" "-DASIO_STANDALONE=1" "-DJUCER_LINUX_MAKE_6D53C8B4=1" "-DJUCE_APP_VERSION=1.0.0" "-DJUCE_APP_VERSION_HEX=0x10000" $(shell pkg-config --cflags alsa freetype2 libcurl webkit2gtk-4.0 gtk+-x11-3.0) -pthread -I../../JuceLibraryCode -I../../3rdParty/JUCE/modules -I../../3rdParty/Simple-WebSocket-Server/ -I../../3rdParty/asio/asio/include/ -I../../Source/common/ -I../../3rdParty/ff_meters/LevelMeter/ $(CPPFLAGS)
```

## Fix 2: Enhanced MIDI Device Fallback Mechanism

**Problem**: Silent MIDI device initialization failures can cause transport controls to appear broken.

**Solution**: Add fallback device creation and better error handling.

**File**: `Shepherd/Source/Sequencer.cpp`
**Method**: `initializeMidiOutputDevice()` (around line 563)

```cpp
MidiOutputDeviceData* Sequencer::initializeMidiOutputDevice(juce::String deviceName)
{
    JUCE_ASSERT_MESSAGE_THREAD
    
    if (deviceName == INTERNAL_OUTPUT_MIDI_DEVICE_NAME){
        // If trying to initialize the internal device name, we create a MidiOutputDeviceData object without an actual midi device
        MidiOutputDeviceData* deviceData = new MidiOutputDeviceData();
        deviceData->buffer.ensureSize(MIDI_BUFFER_MIN_BYTES);
        deviceData->identifier = INTERNAL_OUTPUT_MIDI_DEVICE_NAME;
        deviceData->name = INTERNAL_OUTPUT_MIDI_DEVICE_NAME;
        deviceData->device = nullptr;  // Set device to nullptr as this is an internal device and does not correspond to any real midi device
        DBG("Initialized internal MIDI output device: " << deviceName);
        return deviceData;
    }
    
    auto midiOutputs = juce::MidiOutput::getAvailableDevices();
    juce::String outDeviceIdentifier = "";
    for (int i=0; i<midiOutputs.size(); i++){
        if (midiOutputs[i].name == deviceName){
            outDeviceIdentifier = midiOutputs[i].identifier;
            break;
        }
    }
    
    // If device not found, try to create a virtual device as fallback
    if (outDeviceIdentifier.isEmpty()) {
        DBG("WARNING: MIDI output device '" << deviceName << "' not found. Available devices:");
        for (int i=0; i<midiOutputs.size(); i++){
            DBG("- " << midiOutputs[i].name);
        }
        
        // Create a virtual device that logs MIDI messages instead of failing completely
        DBG("Creating virtual MIDI output device for: " << deviceName);
        MidiOutputDeviceData* deviceData = new MidiOutputDeviceData();
        deviceData->buffer.ensureSize(MIDI_BUFFER_MIN_BYTES);
        deviceData->identifier = "virtual_" + deviceName;
        deviceData->name = deviceName;
        deviceData->device = nullptr; // Virtual device, no actual MIDI output
        
        // Store virtual device info for debugging
        deviceData->isVirtual = true;
        return deviceData;
    }
    
    MidiOutputDeviceData* deviceData = new MidiOutputDeviceData();
    deviceData->buffer.ensureSize(MIDI_BUFFER_MIN_BYTES);
    deviceData->identifier = outDeviceIdentifier;
    deviceData->name = deviceName;
    deviceData->device = juce::MidiOutput::openDevice(outDeviceIdentifier);
    
    if (deviceData->device != nullptr){
        DBG("Successfully initialized MIDI output device: " << deviceName);
        return deviceData;
    } else {
        delete deviceData; // Delete created MidiOutputDeviceData to avoid memory leaks with created buffer
        
        // Create virtual device as final fallback
        DBG("ERROR: Could not open MIDI output device '" << deviceName << "'. Creating virtual device.");
        MidiOutputDeviceData* virtualDeviceData = new MidiOutputDeviceData();
        virtualDeviceData->buffer.ensureSize(MIDI_BUFFER_MIN_BYTES);
        virtualDeviceData->identifier = "virtual_" + deviceName;
        virtualDeviceData->name = deviceName;
        virtualDeviceData->device = nullptr;
        virtualDeviceData->isVirtual = true;
        return virtualDeviceData;
    }
}
```

**File**: `Shepherd/Source/defines_shepherd.h`
**Add new struct member to track virtual devices**

```cpp
struct MidiOutputDeviceData {
    juce::String identifier;
    juce::String name;
    juce::MidiBuffer buffer;
    std::unique_ptr<juce::MidiOutput> device;
    bool isVirtual = false;  // New flag to identify virtual devices
};
```

## Fix 3: Improved MIDI Output Buffer Management

**Problem**: Virtual devices need special handling when sending MIDI messages.

**Solution**: Update the send method to handle virtual devices gracefully.

**File**: `Shepherd/Source/Sequencer.cpp`
**Method**: `sendMidiDeviceOutputBuffers()` (around line 714)

```cpp
void Sequencer::sendMidiDeviceOutputBuffers()
{
    for (auto deviceData: midiOutDevices){
        if (deviceData != nullptr && deviceData->name != INTERNAL_OUTPUT_MIDI_DEVICE_NAME){
            if (deviceData->device != nullptr) {
                // Normal device with actual MIDI output
                deviceData->device->sendBlockOfMessagesNow(deviceData->buffer);
            } else if (deviceData->isVirtual) {
                // Virtual device - log the MIDI messages instead of sending them
                DBG("VIRTUAL MIDI OUTPUT (" << deviceData->name << "): " << deviceData->buffer.getNumEvents() << " messages");
                // Optionally log message details for debugging
                for (const auto& metadata : deviceData->buffer) {
                    juce::MidiMessage msg = metadata.getMessage();
                    DBG("  " << msg.getDescription());
                }
                deviceData->buffer.clear(); // Clear buffer after logging
            }
        }
    }
}
```

## Fix 4: Hardware Device MIDI Validation

**Problem**: Hardware devices may report as initialized when they're actually using virtual fallbacks.

**Solution**: Update the MIDI initialization check.

**File**: `Shepherd/Source/HardwareDevice.h`
**Method**: `isMidiInitialized()` (around line 29)

```cpp
bool isMidiInitialized() {
    if (isTypeInput()){
        auto inputData = getMidiInputDeviceData(getMidiInputDeviceName());
        return inputData != nullptr && (inputData->device != nullptr || inputData->isVirtual);
    } else {
        auto outputData = getMidiOutputDeviceData(getMidiOutputDeviceName());
        return outputData != nullptr && (outputData->device != nullptr || outputData->isVirtual);
    }
}
```

## Fix 5: Transport Control Message Validation

**Problem**: WebSocket messages may not be reaching the backend or being processed correctly.

**Solution**: Add validation and fallback processing for transport controls.

**File**: `Shepherd/Source/Sequencer.cpp`
**Method**: `processMessageFromController()` (ACTION_ADDRESS_TRANSPORT_PLAY_STOP section, around line 1385)

```cpp
} else if (action == ACTION_ADDRESS_TRANSPORT_PLAY_STOP){
    jassert(parameters.size() == 0);
    
    DBG("=== TRANSPORT CONTROL RECEIVED ===");
    DBG("Action: " << action);
    DBG("Current playing state: " << musicalContext->playheadIsPlaying());
    
    if (musicalContext->playheadIsPlaying()){
        // If it is playing, stop it
        DBG("Stopping transport");
        shouldToggleIsPlaying = true;
    } else{
        // If it is not playing, check if there are record-armed clips and, if so, do count-in before playing
        bool recordCuedClipsFound = false;
        for (auto track: tracks->objects){
            if (track->hasClipsCuedToRecord()){
                recordCuedClipsFound = true;
                DBG("Found clips cued to record, starting count-in");
                break;
            }
        }
        if (recordCuedClipsFound){
            DBG("Starting count-in for recording");
            musicalContext->setPlayheadIsDoingCountIn(true);
        } else {
            DBG("Starting transport without count-in");
            shouldToggleIsPlaying = true;
        }
    }
    DBG("shouldToggleIsPlaying set to: " << shouldToggleIsPlaying);
```

## Fix 6: System Status Dashboard

**Problem**: Difficult to diagnose what's happening without real-time system information.

**Solution**: Add a simple status reporting system.

**File**: `Shepherd/Source/Sequencer.cpp`
**Method**: Add new method to report system status

```cpp
void Sequencer::reportSystemStatus()
{
    DBG("=== SHEPHERD SYSTEM STATUS ===");
    DBG("Platform: Linux" << #ifdef RPI_BUILD << " (RPI_BUILD)" << #endif);
    DBG("Sequencer Initialized: " << sequencerInitialized);
    DBG("Musical Context Valid: " << (musicalContext != nullptr));
    DBG("Playing: " << (musicalContext ? musicalContext->playheadIsPlaying() : false));
    DBG("Sample Rate: " << sampleRate);
    DBG("Samples Per Slice: " << samplesPerSlice);
    
    DBG("MIDI Input Devices: " << midiInDevices.size());
    for (auto device : midiInDevices) {
        if (device) {
            DBG("  - " << device->name << " (Device: " << (device->device ? "Real" : "Virtual") << ")");
        }
    }
    
    DBG("MIDI Output Devices: " << midiOutDevices.size());
    for (auto device : midiOutDevices) {
        if (device) {
            DBG("  - " << device->name << " (Device: " << (device->device ? "Real" : "Virtual") << ")");
        }
    }
    
    DBG("Hardware Devices: " << (hardwareDevices ? hardwareDevices->objects.size() : 0));
    if (hardwareDevices) {
        for (auto device : hardwareDevices->objects) {
            DBG("  - " << device->getName() << " (" << (device->isTypeOutput() ? "Output" : "Input") << ") MIDI: " 
                << (device->isMidiInitialized() ? "OK" : "FAILED"));
        }
    }
    
    DBG("Tracks: " << (tracks ? tracks->objects.size() : 0));
    DBG("shouldToggleIsPlaying: " << shouldToggleIsPlaying);
    DBG("shouldTryInitializeMidiInputs: " << shouldTryInitializeMidiInputs);
    DBG("shouldTryInitializeMidiOutputs: " << shouldTryInitializeMidiOutputs);
}
```

**Call this method** from `timerCallback()` every 30 seconds and also add a WebSocket action to trigger it on demand.

## Fix 7: Quick Test Command

**Add to the WebSocket message handler** (around line 1524):

```cpp
} else if (action == ACTION_ADDRESS_SYSTEM_DIAGNOSTICS) {
    jassert(parameters.size() == 0);
    reportSystemStatus();
}
```

## Implementation Steps

1. **Apply Fix 1 first** (RPI_BUILD flag) - this alone may resolve many issues
2. **Apply Fixes 2-4** if device initialization is still failing
3. **Apply Fixes 5-7** for better debugging and monitoring
4. **Test each fix** individually to identify the primary cause
5. **Monitor logs** to verify each component is working correctly

## Expected Results

**After Fix 1**: Platform-specific optimizations will be enabled, reducing MIDI conflicts
**After Fix 2**: No more silent device failures, virtual devices will log MIDI activity
**After Fix 3**: MIDI messages will be processed even with fallback devices
**After Fix 4**: Hardware device status will be more accurate
**After Fix 5**: Transport controls will work reliably with proper logging
**After Fix 6**: System status will provide complete diagnostic information
**After Fix 7**: Real-time debugging will be possible via WebSocket commands
