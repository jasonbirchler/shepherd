#include <iostream>
#include <string>
#include <functional>
#include "mocks.h"

// Simple test framework
struct TestResult {
    bool passed = true;
    std::string message;
};

class TestRunner {
public:
    static void run(const std::string& testName, std::function<TestResult()> test) {
        std::cout << "Running " << testName << "... ";
        auto result = test();
        if (result.passed) {
            std::cout << "PASS" << std::endl;
            passCount++;
        } else {
            std::cout << "FAIL: " << result.message << std::endl;
            failCount++;
        }
        totalCount++;
    }
    
    static void printSummary() {
        std::cout << "\nTest Summary: " << passCount << "/" << totalCount << " passed";
        if (failCount > 0) {
            std::cout << " (" << failCount << " failed)";
        }
        std::cout << std::endl;
    }
    
    static int getFailCount() { return failCount; }
    
private:
    static int totalCount;
    static int passCount;
    static int failCount;
};

int TestRunner::totalCount = 0;
int TestRunner::passCount = 0;
int TestRunner::failCount = 0;

void runMockTests() {
    TestRunner::run("Mock MIDI Device Manager", []() {
        MockMidiDeviceManager manager;
        
        // Add devices
        manager.addOutputDevice("Test Synth");
        manager.addInputDevice("Test Controller");
        
        // Test device retrieval
        auto* outputDevice = manager.getOutputDevice("Test Synth");
        auto* inputDevice = manager.getInputDevice("Test Controller");
        
        if (!outputDevice || outputDevice->name != "Test Synth") {
            return TestResult{false, "Output device not created correctly"};
        }
        
        if (!inputDevice || inputDevice->name != "Test Controller") {
            return TestResult{false, "Input device not created correctly"};
        }
        
        // Test MIDI message sending
        MockMidiMessage msg(1, 60, 127);
        outputDevice->sendMessage(msg);
        
        if (outputDevice->sentMessages.size() != 1) {
            return TestResult{false, "MIDI message not sent"};
        }
        
        if (outputDevice->sentMessages[0].note != 60) {
            return TestResult{false, "MIDI message data incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Mock WebSocket Connection", []() {
        MockWebSocketConnection connection;
        
        // Test connection state
        if (connection.isConnected) {
            return TestResult{false, "Connection should start disconnected"};
        }
        
        connection.connect();
        if (!connection.isConnected) {
            return TestResult{false, "Connection failed to connect"};
        }
        
        // Test message sending
        connection.send("/test/address", "test data");
        
        if (connection.sentMessages.size() != 1) {
            return TestResult{false, "Message not sent"};
        }
        
        if (connection.sentMessages[0].address != "/test/address") {
            return TestResult{false, "Message address incorrect"};
        }
        
        // Test message receiving
        bool messageReceived = false;
        connection.setMessageHandler([&messageReceived](const MockWebSocketMessage& msg) {
            messageReceived = (msg.address == "/incoming/test");
        });
        
        connection.simulateReceive("/incoming/test", "incoming data");
        
        if (!messageReceived) {
            return TestResult{false, "Message handler not called"};
        }
        
        if (connection.receivedMessages.size() != 1) {
            return TestResult{false, "Received message not stored"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Mock Timer", []() {
        MockTimer timer;
        
        if (timer.getCurrentTime() != 0.0) {
            return TestResult{false, "Timer should start at 0"};
        }
        
        timer.advance(1.5);
        if (timer.getCurrentTime() != 1.5) {
            return TestResult{false, "Timer advance not working"};
        }
        
        timer.reset();
        if (timer.getCurrentTime() != 0.0) {
            return TestResult{false, "Timer reset not working"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Mock Global Settings", []() {
        auto& settings = MockGlobalSettings::getInstance();
        
        if (settings.sampleRate != 44100.0) {
            return TestResult{false, "Default sample rate incorrect"};
        }
        
        if (settings.samplesPerSlice != 512) {
            return TestResult{false, "Default samples per slice incorrect"};
        }
        
        // Test singleton behavior
        auto& settings2 = MockGlobalSettings::getInstance();
        settings2.sampleRate = 48000.0;
        
        if (settings.sampleRate != 48000.0) {
            return TestResult{false, "Singleton not working correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("MIDI Channel Validation with Mocks", []() {
        MockMidiDeviceManager manager;
        manager.addOutputDevice("Test Device");
        auto* device = manager.getOutputDevice("Test Device");
        
        // Test valid MIDI channels
        for (int channel = 1; channel <= 16; channel++) {
            MockMidiMessage msg(channel, 60, 127);
            device->sendMessage(msg);
        }
        
        if (device->sentMessages.size() != 16) {
            return TestResult{false, "Not all valid MIDI channels accepted"};
        }
        
        // Verify channel values
        for (size_t i = 0; i < device->sentMessages.size(); i++) {
            if (device->sentMessages[i].channel != (int)(i + 1)) {
                return TestResult{false, "MIDI channel values incorrect"};
            }
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd Mock Framework Tests" << std::endl;
    std::cout << "=============================" << std::endl;
    
    runMockTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}