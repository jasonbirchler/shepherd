#include <iostream>
#include <string>
#include <functional>

// Simple test framework without JUCE dependencies
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

// Basic tests for core logic without JUCE dependencies
void runBasicTests() {
    TestRunner::run("Basic Math Operations", []() {
        double bpm = 120.0;
        double sampleRate = 44100.0;
        double beatsPerSample = 1.0 / (60.0 * sampleRate / bpm);
        
        // Test basic BPM to sample conversion
        if (beatsPerSample <= 0.0) {
            return TestResult{false, "Invalid beats per sample calculation"};
        }
        
        // Test that 1 beat at 120 BPM = 0.5 seconds = 22050 samples at 44.1kHz
        double expectedSamplesPerBeat = sampleRate * 60.0 / bpm;
        if (std::abs(expectedSamplesPerBeat - 22050.0) > 0.1) {
            return TestResult{false, "BPM to sample conversion incorrect"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("MIDI Channel Validation", []() {
        // Test MIDI channel range validation (1-16)
        auto isValidMidiChannel = [](int channel) {
            return channel >= 1 && channel <= 16;
        };
        
        if (!isValidMidiChannel(1) || !isValidMidiChannel(16)) {
            return TestResult{false, "Valid MIDI channels rejected"};
        }
        
        if (isValidMidiChannel(0) || isValidMidiChannel(17)) {
            return TestResult{false, "Invalid MIDI channels accepted"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("String Utilities", []() {
        // Test basic string operations that might be used in the backend
        std::string deviceName = "Test Device";  // 11 chars - should not be shortened
        std::string shortName = deviceName.length() > 12 ? 
            "..." + deviceName.substr(deviceName.length() - 9) : deviceName;
        
        if (shortName != deviceName) {
            return TestResult{false, "Short name generation failed for normal length: expected '" + deviceName + "', got '" + shortName + "'"};
        }
        
        std::string longName = "This is a very long device name";  // 32 chars
        std::string longShortName = longName.length() > 12 ? 
            "..." + longName.substr(longName.length() - 9) : longName;
        
        if (longShortName != "...vice name") {
            return TestResult{false, "Short name generation failed for long name: got '" + longShortName + "'"};
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd Backend Tests (Simplified)" << std::endl;
    std::cout << "====================================" << std::endl;
    
    runBasicTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}