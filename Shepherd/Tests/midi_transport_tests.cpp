#include <iostream>
#include <string>
#include <functional>
#include <vector>
#include <map>
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

// MIDI Clock Message Types
enum MidiClockType {
    CLOCK_TICK = 0xF8,      // 24 PPQ timing clock
    START = 0xFA,           // Start transport
    CONTINUE = 0xFB,        // Continue transport
    STOP = 0xFC             // Stop transport
};

// Mock MIDI Clock Message
struct MockMidiClockMessage {
    MidiClockType type;
    double timestamp;
    
    MockMidiClockMessage(MidiClockType t, double ts = 0.0) : type(t), timestamp(ts) {}
};

// Mock Sequencer with transport separation
class MockSequencer {
private:
    std::vector<std::string> clockDevices;
    std::vector<std::string> transportDevices;
    MockMidiDeviceManager* deviceManager;
    bool isPlaying = false;
    double bpm = 120.0;
    int clockTickCount = 0;
    
public:
    MockSequencer(MockMidiDeviceManager* dm) : deviceManager(dm) {}
    
    void setClockDevices(const std::vector<std::string>& devices) {
        clockDevices = devices;
    }
    
    void setTransportDevices(const std::vector<std::string>& devices) {
        transportDevices = devices;
    }
    
    void start() {
        isPlaying = true;
        sendTransportMessage(START);
    }
    
    void stop() {
        isPlaying = false;
        sendTransportMessage(STOP);
    }
    
    void continue_() {
        isPlaying = true;
        sendTransportMessage(CONTINUE);
    }
    
    void generateClockTicks(int numTicks) {
        if (isPlaying) {
            for (int i = 0; i < numTicks; i++) {
                sendClockMessage(CLOCK_TICK);
                clockTickCount++;
            }
        }
    }
    
    int getClockTickCount() const { return clockTickCount; }
    bool getIsPlaying() const { return isPlaying; }
    
private:
    void sendClockMessage(MidiClockType type) {
        for (const auto& deviceName : clockDevices) {
            auto* device = deviceManager->getOutputDevice(deviceName);
            if (device) {
                MockMidiMessage msg;
                msg.rawData = {static_cast<uint8_t>(type)};
                device->sendMessage(msg);
            }
        }
    }
    
    void sendTransportMessage(MidiClockType type) {
        for (const auto& deviceName : transportDevices) {
            auto* device = deviceManager->getOutputDevice(deviceName);
            if (device) {
                MockMidiMessage msg;
                msg.rawData = {static_cast<uint8_t>(type)};
                device->sendMessage(msg);
            }
        }
    }
};

void runMidiTransportTests() {
    TestRunner::run("Transport Separation - Clock Only Device", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("ClockOnly");
        deviceManager.addOutputDevice("TransportOnly");
        
        MockSequencer sequencer(&deviceManager);
        sequencer.setClockDevices({"ClockOnly"});
        sequencer.setTransportDevices({"TransportOnly"});
        
        // Start sequencer and generate clock ticks
        sequencer.start();
        sequencer.generateClockTicks(24); // One beat at 24 PPQ
        
        auto* clockDevice = deviceManager.getOutputDevice("ClockOnly");
        auto* transportDevice = deviceManager.getOutputDevice("TransportOnly");
        
        // Clock device should receive 24 clock ticks but no transport messages
        if (clockDevice->sentMessages.size() != 24) {
            return TestResult{false, "Clock device didn't receive correct number of clock ticks"};
        }
        
        // Transport device should receive only start message
        if (transportDevice->sentMessages.size() != 1) {
            return TestResult{false, "Transport device didn't receive exactly one message"};
        }
        
        if (transportDevice->sentMessages[0].rawData[0] != START) {
            return TestResult{false, "Transport device didn't receive START message"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Both Messages Device", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("BothMessages");
        
        MockSequencer sequencer(&deviceManager);
        sequencer.setClockDevices({"BothMessages"});
        sequencer.setTransportDevices({"BothMessages"});
        
        // Start and generate some clock ticks
        sequencer.start();
        sequencer.generateClockTicks(12);
        sequencer.stop();
        
        auto* device = deviceManager.getOutputDevice("BothMessages");
        
        // Should receive: START + 12 clock ticks + STOP = 14 messages
        if (device->sentMessages.size() != 14) {
            return TestResult{false, "Device didn't receive correct total number of messages"};
        }
        
        // First message should be START
        if (device->sentMessages[0].rawData[0] != START) {
            return TestResult{false, "First message wasn't START"};
        }
        
        // Middle messages should be clock ticks
        for (int i = 1; i <= 12; i++) {
            if (device->sentMessages[i].rawData[0] != CLOCK_TICK) {
                return TestResult{false, "Clock tick message incorrect at position " + std::to_string(i)};
            }
        }
        
        // Last message should be STOP
        if (device->sentMessages[13].rawData[0] != STOP) {
            return TestResult{false, "Last message wasn't STOP"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Multiple Devices", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("Device1");
        deviceManager.addOutputDevice("Device2");
        deviceManager.addOutputDevice("Device3");
        
        MockSequencer sequencer(&deviceManager);
        // Device1 gets both, Device2 gets clock only, Device3 gets transport only
        sequencer.setClockDevices({"Device1", "Device2"});
        sequencer.setTransportDevices({"Device1", "Device3"});
        
        sequencer.start();
        sequencer.generateClockTicks(6);
        sequencer.stop();
        
        auto* device1 = deviceManager.getOutputDevice("Device1");
        auto* device2 = deviceManager.getOutputDevice("Device2");
        auto* device3 = deviceManager.getOutputDevice("Device3");
        
        // Device1: START + 6 clocks + STOP = 8 messages
        if (device1->sentMessages.size() != 8) {
            return TestResult{false, "Device1 message count incorrect"};
        }
        
        // Device2: 6 clocks only
        if (device2->sentMessages.size() != 6) {
            return TestResult{false, "Device2 message count incorrect"};
        }
        
        // Device3: START + STOP = 2 messages
        if (device3->sentMessages.size() != 2) {
            return TestResult{false, "Device3 message count incorrect"};
        }
        
        // Verify Device2 only got clock ticks
        for (const auto& msg : device2->sentMessages) {
            if (msg.rawData[0] != CLOCK_TICK) {
                return TestResult{false, "Device2 received non-clock message"};
            }
        }
        
        // Verify Device3 only got transport messages
        if (device3->sentMessages[0].rawData[0] != START || 
            device3->sentMessages[1].rawData[0] != STOP) {
            return TestResult{false, "Device3 transport messages incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Continue Command", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("TransportDevice");
        
        MockSequencer sequencer(&deviceManager);
        sequencer.setTransportDevices({"TransportDevice"});
        
        // Test start -> stop -> continue sequence
        sequencer.start();
        sequencer.stop();
        sequencer.continue_();
        
        auto* device = deviceManager.getOutputDevice("TransportDevice");
        
        if (device->sentMessages.size() != 3) {
            return TestResult{false, "Incorrect number of transport messages"};
        }
        
        if (device->sentMessages[0].rawData[0] != START ||
            device->sentMessages[1].rawData[0] != STOP ||
            device->sentMessages[2].rawData[0] != CONTINUE) {
            return TestResult{false, "Transport message sequence incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Empty Device Lists", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("UnusedDevice");
        
        MockSequencer sequencer(&deviceManager);
        // No devices configured for clock or transport
        
        sequencer.start();
        sequencer.generateClockTicks(10);
        sequencer.stop();
        
        auto* device = deviceManager.getOutputDevice("UnusedDevice");
        
        // Device should receive no messages
        if (device->sentMessages.size() != 0) {
            return TestResult{false, "Device received messages when none should be sent"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Nonexistent Devices", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("RealDevice");
        
        MockSequencer sequencer(&deviceManager);
        // Configure with mix of real and nonexistent devices
        sequencer.setClockDevices({"RealDevice", "FakeDevice1"});
        sequencer.setTransportDevices({"FakeDevice2", "RealDevice"});
        
        sequencer.start();
        sequencer.generateClockTicks(3);
        
        auto* realDevice = deviceManager.getOutputDevice("RealDevice");
        
        // Real device should receive: START + 3 clocks = 4 messages
        if (realDevice->sentMessages.size() != 4) {
            return TestResult{false, "Real device didn't receive correct messages despite fake devices in config"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Transport Separation - Clock Timing Accuracy", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("ClockDevice");
        
        MockSequencer sequencer(&deviceManager);
        sequencer.setClockDevices({"ClockDevice"});
        
        sequencer.start();
        
        // Generate exactly 96 ticks (4 beats at 24 PPQ)
        sequencer.generateClockTicks(96);
        
        auto* device = deviceManager.getOutputDevice("ClockDevice");
        
        if (device->sentMessages.size() != 96) {
            return TestResult{false, "Clock tick count doesn't match expected 96 ticks"};
        }
        
        // Verify all messages are clock ticks
        for (const auto& msg : device->sentMessages) {
            if (msg.rawData[0] != CLOCK_TICK) {
                return TestResult{false, "Non-clock message found in clock stream"};
            }
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd MIDI Transport Separation Tests" << std::endl;
    std::cout << "========================================" << std::endl;
    
    runMidiTransportTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}