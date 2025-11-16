#include "../JuceLibraryCode/JuceHeader.h"
#include "HardwareDevice.h"
#include "helpers_shepherd.h"

extern void TestRunner::run(const juce::String&, std::function<TestResult()>);

// Mock MIDI device data
MidiOutputDeviceData* mockMidiOutputDeviceData(juce::String deviceName) {
    return nullptr; // For basic tests, we don't need actual MIDI devices
}

MidiInputDeviceData* mockMidiInputDeviceData(juce::String deviceName) {
    return nullptr; // For basic tests, we don't need actual MIDI devices
}

void runHardwareDeviceTests() {
    TestRunner::run("HardwareDevice - Output Device Creation", []() {
        juce::ValueTree state(ShepherdIDs::HARDWARE_DEVICE);
        state.setProperty(ShepherdIDs::uuid, "test-device-1", nullptr);
        state.setProperty(ShepherdIDs::type, (int)HardwareDeviceType::output, nullptr);
        state.setProperty(ShepherdIDs::name, "Test Output Device", nullptr);
        state.setProperty(ShepherdIDs::shortName, "TestOut", nullptr);
        state.setProperty(ShepherdIDs::midiOutputDeviceName, "Mock MIDI Out", nullptr);
        state.setProperty(ShepherdIDs::midiOutputChannel, 1, nullptr);
        
        HardwareDevice device(state, mockMidiOutputDeviceData, mockMidiInputDeviceData);
        
        if (!device.isTypeOutput()) {
            return TestResult{false, "Device should be output type"};
        }
        if (device.isTypeInput()) {
            return TestResult{false, "Device should not be input type"};
        }
        if (device.getName() != "Test Output Device") {
            return TestResult{false, "Device name not set correctly"};
        }
        if (device.getShortName() != "TestOut") {
            return TestResult{false, "Device short name not set correctly"};
        }
        if (device.getMidiOutputChannel() != 1) {
            return TestResult{false, "MIDI output channel not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("HardwareDevice - Input Device Creation", []() {
        juce::ValueTree state(ShepherdIDs::HARDWARE_DEVICE);
        state.setProperty(ShepherdIDs::uuid, "test-device-2", nullptr);
        state.setProperty(ShepherdIDs::type, (int)HardwareDeviceType::input, nullptr);
        state.setProperty(ShepherdIDs::name, "Test Input Device", nullptr);
        state.setProperty(ShepherdIDs::shortName, "TestIn", nullptr);
        state.setProperty(ShepherdIDs::midiInputDeviceName, "Mock MIDI In", nullptr);
        
        HardwareDevice device(state, mockMidiOutputDeviceData, mockMidiInputDeviceData);
        
        if (!device.isTypeInput()) {
            return TestResult{false, "Device should be input type"};
        }
        if (device.isTypeOutput()) {
            return TestResult{false, "Device should not be output type"};
        }
        if (device.getName() != "Test Input Device") {
            return TestResult{false, "Device name not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("HardwareDevice - UUID Handling", []() {
        juce::ValueTree state(ShepherdIDs::HARDWARE_DEVICE);
        state.setProperty(ShepherdIDs::uuid, "unique-test-id-123", nullptr);
        state.setProperty(ShepherdIDs::type, (int)HardwareDeviceType::output, nullptr);
        state.setProperty(ShepherdIDs::name, "UUID Test Device", nullptr);
        
        HardwareDevice device(state, mockMidiOutputDeviceData, mockMidiInputDeviceData);
        
        if (device.getUUID() != "unique-test-id-123") {
            return TestResult{false, "UUID not handled correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("HardwareDeviceList - Device Management", []() {
        juce::ValueTree parentState(ShepherdIDs::HARDWARE_DEVICES);
        
        // Add output device
        juce::ValueTree outputDevice(ShepherdIDs::HARDWARE_DEVICE);
        outputDevice.setProperty(ShepherdIDs::uuid, "output-1", nullptr);
        outputDevice.setProperty(ShepherdIDs::type, (int)HardwareDeviceType::output, nullptr);
        outputDevice.setProperty(ShepherdIDs::name, "Output Device 1", nullptr);
        parentState.appendChild(outputDevice, nullptr);
        
        // Add input device
        juce::ValueTree inputDevice(ShepherdIDs::HARDWARE_DEVICE);
        inputDevice.setProperty(ShepherdIDs::uuid, "input-1", nullptr);
        inputDevice.setProperty(ShepherdIDs::type, (int)HardwareDeviceType::input, nullptr);
        inputDevice.setProperty(ShepherdIDs::name, "Input Device 1", nullptr);
        parentState.appendChild(inputDevice, nullptr);
        
        HardwareDeviceList deviceList(parentState, mockMidiOutputDeviceData, mockMidiInputDeviceData);
        
        auto outputNames = deviceList.getAvailableOutputHardwareDeviceNames();
        auto inputNames = deviceList.getAvailableInputHardwareDeviceNames();
        
        if (outputNames.size() != 1 || outputNames[0] != "Output Device 1") {
            return TestResult{false, "Output device list not correct"};
        }
        if (inputNames.size() != 1 || inputNames[0] != "Input Device 1") {
            return TestResult{false, "Input device list not correct"};
        }
        
        auto* foundDevice = deviceList.getObjectWithUUID("output-1");
        if (!foundDevice || foundDevice->getName() != "Output Device 1") {
            return TestResult{false, "Device lookup by UUID failed"};
        }
        
        return TestResult{true, ""};
    });
}