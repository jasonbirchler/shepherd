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

// Mock MusicalContext using mocks
class MockMusicalContext {
private:
    double bpm = 120.0;
    int meter = 4;
    double playheadPosition = 0.0;
    bool playing = false;
    bool metronomeOn = false;
    MockTimer* timer;
    
public:
    MockMusicalContext(MockTimer* t) : timer(t) {}
    
    void setBpm(double newBpm) { 
        if (newBpm > 0) bpm = newBpm; 
    }
    double getBpm() const { return bpm; }
    
    void setMeter(int newMeter) { 
        if (newMeter > 0) meter = newMeter; 
    }
    int getMeter() const { return meter; }
    
    void setPlayheadPosition(double pos) { playheadPosition = pos; }
    double getPlayheadPosition() const { return playheadPosition; }
    
    void setPlaying(bool isPlaying) { playing = isPlaying; }
    bool isPlaying() const { return playing; }
    
    void setMetronome(bool on) { metronomeOn = on; }
    bool getMetronome() const { return metronomeOn; }
    
    void advance(double beats) {
        if (playing) {
            playheadPosition += beats;
            timer->advance(beats * 60.0 / bpm); // Convert beats to seconds
        }
    }
};

// Mock Track with hardware device assignment
class MockTrack {
private:
    std::string name;
    std::string hardwareDeviceName;
    MockMidiDeviceManager* deviceManager;
    
public:
    MockTrack(const std::string& trackName, MockMidiDeviceManager* dm) 
        : name(trackName), deviceManager(dm) {}
    
    void setHardwareDevice(const std::string& deviceName) {
        auto* device = deviceManager->getOutputDevice(deviceName);
        if (device) {
            hardwareDeviceName = deviceName;
        }
    }
    
    std::string getHardwareDevice() const { return hardwareDeviceName; }
    
    void sendMidiNote(int note, int velocity, int channel = 1) {
        auto* device = deviceManager->getOutputDevice(hardwareDeviceName);
        if (device) {
            MockMidiMessage msg(channel, note, velocity);
            device->sendMessage(msg);
        }
    }
};

void runBackendComponentTests() {
    TestRunner::run("MusicalContext - BPM and Timing", []() {
        MockTimer timer;
        MockMusicalContext context(&timer);
        
        // Test BPM changes
        context.setBpm(140.0);
        if (context.getBpm() != 140.0) {
            return TestResult{false, "BPM not set correctly"};
        }
        
        // Test invalid BPM rejected
        context.setBpm(-10.0);
        if (context.getBpm() != 140.0) {
            return TestResult{false, "Invalid BPM was accepted"};
        }
        
        // Test playhead advancement
        context.setPlaying(true);
        context.advance(2.0); // 2 beats
        
        if (context.getPlayheadPosition() != 2.0) {
            return TestResult{false, "Playhead not advanced correctly"};
        }
        
        // Test timing calculation (2 beats at 140 BPM = ~0.857 seconds)
        double expectedTime = 2.0 * 60.0 / 140.0;
        if (std::abs(timer.getCurrentTime() - expectedTime) > 0.001) {
            return TestResult{false, "Timer not advanced correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Meter and Metronome", []() {
        MockTimer timer;
        MockMusicalContext context(&timer);
        
        // Test meter changes
        context.setMeter(3);
        if (context.getMeter() != 3) {
            return TestResult{false, "Meter not set correctly"};
        }
        
        // Test metronome control
        context.setMetronome(true);
        if (!context.getMetronome()) {
            return TestResult{false, "Metronome not enabled"};
        }
        
        context.setMetronome(false);
        if (context.getMetronome()) {
            return TestResult{false, "Metronome not disabled"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Track - Hardware Device Assignment", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("Synth 1");
        deviceManager.addOutputDevice("Synth 2");
        
        MockTrack track("Track 1", &deviceManager);
        
        // Test device assignment
        track.setHardwareDevice("Synth 1");
        if (track.getHardwareDevice() != "Synth 1") {
            return TestResult{false, "Hardware device not assigned correctly"};
        }
        
        // Test device switching
        track.setHardwareDevice("Synth 2");
        if (track.getHardwareDevice() != "Synth 2") {
            return TestResult{false, "Hardware device not switched correctly"};
        }
        
        // Test invalid device assignment (should not change)
        track.setHardwareDevice("NonExistent");
        if (track.getHardwareDevice() != "Synth 2") {
            return TestResult{false, "Invalid device assignment changed current device"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Track - MIDI Message Routing", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("Test Synth");
        
        MockTrack track("Track 1", &deviceManager);
        track.setHardwareDevice("Test Synth");
        
        // Send MIDI note
        track.sendMidiNote(60, 127, 1);
        
        auto* device = deviceManager.getOutputDevice("Test Synth");
        if (!device || device->sentMessages.size() != 1) {
            return TestResult{false, "MIDI message not sent to device"};
        }
        
        auto& msg = device->sentMessages[0];
        if (msg.note != 60 || msg.velocity != 127 || msg.channel != 1) {
            return TestResult{false, "MIDI message data incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Session - Multi-Track Coordination", []() {
        MockMidiDeviceManager deviceManager;
        MockTimer timer;
        MockMusicalContext context(&timer);
        
        // Setup devices
        deviceManager.addOutputDevice("Synth 1");
        deviceManager.addOutputDevice("Synth 2");
        
        // Setup tracks
        MockTrack track1("Track 1", &deviceManager);
        MockTrack track2("Track 2", &deviceManager);
        track1.setHardwareDevice("Synth 1");
        track2.setHardwareDevice("Synth 2");
        
        // Start session
        context.setPlaying(true);
        context.setBpm(120.0);
        
        // Send notes from both tracks
        track1.sendMidiNote(60, 100, 1);
        track2.sendMidiNote(64, 110, 2);
        
        // Advance time
        context.advance(1.0);
        
        // Verify both devices received messages
        auto* device1 = deviceManager.getOutputDevice("Synth 1");
        auto* device2 = deviceManager.getOutputDevice("Synth 2");
        
        if (!device1 || device1->sentMessages.size() != 1) {
            return TestResult{false, "Track 1 message not sent"};
        }
        
        if (!device2 || device2->sentMessages.size() != 1) {
            return TestResult{false, "Track 2 message not sent"};
        }
        
        // Verify message routing
        if (device1->sentMessages[0].note != 60 || device1->sentMessages[0].channel != 1) {
            return TestResult{false, "Track 1 message routing incorrect"};
        }
        
        if (device2->sentMessages[0].note != 64 || device2->sentMessages[0].channel != 2) {
            return TestResult{false, "Track 2 message routing incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Hardware Device - Channel Management", []() {
        MockMidiDeviceManager deviceManager;
        deviceManager.addOutputDevice("Multi Channel Synth");
        
        auto* device = deviceManager.getOutputDevice("Multi Channel Synth");
        
        // Test multiple channels
        for (int channel = 1; channel <= 16; channel++) {
            MockMidiMessage msg(channel, 60, 100);
            device->sendMessage(msg);
        }
        
        if (device->sentMessages.size() != 16) {
            return TestResult{false, "Not all channel messages sent"};
        }
        
        // Verify channel assignment
        for (int i = 0; i < 16; i++) {
            if (device->sentMessages[i].channel != (i + 1)) {
                return TestResult{false, "Channel assignment incorrect"};
            }
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd Backend Component Tests" << std::endl;
    std::cout << "================================" << std::endl;
    
    runBackendComponentTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}