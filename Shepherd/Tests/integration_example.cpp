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

// Example: Mock-based testing of MIDI channel change functionality
class MockHardwareDeviceController {
private:
    MockMidiDeviceManager* deviceManager;
    MockWebSocketConnection* wsConnection;
    
public:
    MockHardwareDeviceController(MockMidiDeviceManager* dm, MockWebSocketConnection* ws) 
        : deviceManager(dm), wsConnection(ws) {}
    
    bool setDeviceMidiChannel(const std::string& deviceName, int newChannel) {
        // Validate channel range
        if (newChannel < 1 || newChannel > 16) {
            return false;
        }
        
        // Get device
        auto* device = deviceManager->getOutputDevice(deviceName);
        if (!device) {
            return false;
        }
        
        // Send WebSocket message to backend
        std::string message = "{\"device\":\"" + deviceName + "\",\"channel\":" + std::to_string(newChannel) + "}";
        wsConnection->send("/device/setMidiChannel", message);
        
        return true;
    }
    
    void simulateBackendResponse(const std::string& deviceName, int newChannel) {
        // Simulate backend confirming the change
        std::string response = "{\"device\":\"" + deviceName + "\",\"channel\":" + std::to_string(newChannel) + ",\"status\":\"success\"}";
        wsConnection->simulateReceive("/device/channelChanged", response);
    }
};

void runIntegrationTests() {
    TestRunner::run("MIDI Channel Change Integration", []() {
        MockMidiDeviceManager deviceManager;
        MockWebSocketConnection wsConnection;
        MockHardwareDeviceController controller(&deviceManager, &wsConnection);
        
        // Setup
        deviceManager.addOutputDevice("Test Synth");
        wsConnection.connect();
        
        // Test valid channel change
        bool result = controller.setDeviceMidiChannel("Test Synth", 5);
        if (!result) {
            return TestResult{false, "Valid channel change rejected"};
        }
        
        // Verify WebSocket message was sent
        if (wsConnection.sentMessages.size() != 1) {
            return TestResult{false, "WebSocket message not sent"};
        }
        
        auto& sentMsg = wsConnection.sentMessages[0];
        if (sentMsg.address != "/device/setMidiChannel") {
            return TestResult{false, "Wrong WebSocket address"};
        }
        
        if (sentMsg.data.find("\"channel\":5") == std::string::npos) {
            return TestResult{false, "Channel value not in message"};
        }
        
        // Test invalid channel
        bool invalidResult = controller.setDeviceMidiChannel("Test Synth", 17);
        if (invalidResult) {
            return TestResult{false, "Invalid channel change accepted"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Multi-Device MIDI Routing", []() {
        MockMidiDeviceManager deviceManager;
        MockTimer timer;
        
        // Setup multiple devices
        deviceManager.addOutputDevice("Synth 1");
        deviceManager.addOutputDevice("Synth 2");
        deviceManager.addInputDevice("Controller");
        
        auto* synth1 = deviceManager.getOutputDevice("Synth 1");
        auto* synth2 = deviceManager.getOutputDevice("Synth 2");
        auto* controller = deviceManager.getInputDevice("Controller");
        
        // Simulate incoming MIDI from controller
        MockMidiMessage incomingNote(1, 60, 127);
        timer.advance(0.1);
        incomingNote.timestamp = timer.getCurrentTime();
        controller->receiveMessage(incomingNote);
        
        // Route to both synths with different channels
        MockMidiMessage toSynth1(1, 60, 127);
        MockMidiMessage toSynth2(2, 60, 127);
        
        timer.advance(0.001); // Small processing delay
        toSynth1.timestamp = timer.getCurrentTime();
        toSynth2.timestamp = timer.getCurrentTime();
        
        synth1->sendMessage(toSynth1);
        synth2->sendMessage(toSynth2);
        
        // Verify routing
        if (synth1->sentMessages.size() != 1 || synth2->sentMessages.size() != 1) {
            return TestResult{false, "Messages not routed to both synths"};
        }
        
        if (synth1->sentMessages[0].channel != 1 || synth2->sentMessages[0].channel != 2) {
            return TestResult{false, "Channel routing incorrect"};
        }
        
        // Verify timing
        double processingDelay = synth1->sentMessages[0].timestamp - controller->receivedMessages[0].timestamp;
        if (processingDelay <= 0.0 || processingDelay > 0.01) {
            return TestResult{false, "Processing delay out of expected range"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("WebSocket State Synchronization", []() {
        MockWebSocketConnection wsConnection;
        
        // Track state changes
        std::vector<std::string> stateUpdates;
        wsConnection.setMessageHandler([&stateUpdates](const MockWebSocketMessage& msg) {
            if (msg.address == "/state/update") {
                stateUpdates.push_back(msg.data);
            }
        });
        
        wsConnection.connect();
        
        // Simulate backend state changes
        wsConnection.simulateReceive("/state/update", "{\"bpm\":120}");
        wsConnection.simulateReceive("/state/update", "{\"playing\":true}");
        wsConnection.simulateReceive("/state/update", "{\"bpm\":140}");
        
        if (stateUpdates.size() != 3) {
            return TestResult{false, "Not all state updates received"};
        }
        
        if (stateUpdates[0].find("\"bpm\":120") == std::string::npos) {
            return TestResult{false, "First BPM update incorrect"};
        }
        
        if (stateUpdates[2].find("\"bpm\":140") == std::string::npos) {
            return TestResult{false, "BPM change update incorrect"};
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd Integration Tests (Mock-based)" << std::endl;
    std::cout << "=======================================" << std::endl;
    
    runIntegrationTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}