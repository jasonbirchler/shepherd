#include <iostream>
#include <string>
#include <functional>
#include <vector>
#include <map>
#include <fstream>
#include <sstream>

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

// Mock JSON parser for backend settings
class MockBackendSettings {
private:
    std::map<std::string, std::string> stringSettings;
    std::map<std::string, std::vector<std::string>> arraySettings;
    
public:
    bool loadFromString(const std::string& jsonString) {
        // Simple JSON parsing for test purposes
        // In real implementation, this would use proper JSON library
        
        // Parse midiDevicesToSendClockTo array
        size_t clockPos = jsonString.find("\"midiDevicesToSendClockTo\"");
        if (clockPos != std::string::npos) {
            size_t arrayStart = jsonString.find("[", clockPos);
            size_t arrayEnd = jsonString.find("]", arrayStart);
            if (arrayStart != std::string::npos && arrayEnd != std::string::npos) {
                std::string arrayContent = jsonString.substr(arrayStart + 1, arrayEnd - arrayStart - 1);
                arraySettings["midiDevicesToSendClockTo"] = parseStringArray(arrayContent);
            }
        }
        
        // Parse midiDevicesToSendTransportTo array
        size_t transportPos = jsonString.find("\"midiDevicesToSendTransportTo\"");
        if (transportPos != std::string::npos) {
            size_t arrayStart = jsonString.find("[", transportPos);
            size_t arrayEnd = jsonString.find("]", arrayStart);
            if (arrayStart != std::string::npos && arrayEnd != std::string::npos) {
                std::string arrayContent = jsonString.substr(arrayStart + 1, arrayEnd - arrayStart - 1);
                arraySettings["midiDevicesToSendTransportTo"] = parseStringArray(arrayContent);
            }
        }
        
        // Parse pushClockDeviceName
        size_t pushPos = jsonString.find("\"pushClockDeviceName\"");
        if (pushPos != std::string::npos) {
            size_t colonPos = jsonString.find(":", pushPos);
            size_t valueStart = jsonString.find("\"", colonPos);
            size_t valueEnd = jsonString.find("\"", valueStart + 1);
            if (valueStart != std::string::npos && valueEnd != std::string::npos) {
                stringSettings["pushClockDeviceName"] = jsonString.substr(valueStart + 1, valueEnd - valueStart - 1);
            }
        }
        
        return true;
    }
    
    std::vector<std::string> getClockDevices() const {
        auto it = arraySettings.find("midiDevicesToSendClockTo");
        return it != arraySettings.end() ? it->second : std::vector<std::string>();
    }
    
    std::vector<std::string> getTransportDevices() const {
        auto it = arraySettings.find("midiDevicesToSendTransportTo");
        return it != arraySettings.end() ? it->second : std::vector<std::string>();
    }
    
    std::string getPushClockDevice() const {
        auto it = stringSettings.find("pushClockDeviceName");
        return it != stringSettings.end() ? it->second : "";
    }
    
private:
    std::vector<std::string> parseStringArray(const std::string& content) {
        std::vector<std::string> result;
        std::stringstream ss(content);
        std::string item;
        
        while (std::getline(ss, item, ',')) {
            // Remove quotes and whitespace
            size_t start = item.find_first_of("\"");
            size_t end = item.find_last_of("\"");
            if (start != std::string::npos && end != std::string::npos && start < end) {
                result.push_back(item.substr(start + 1, end - start - 1));
            }
        }
        
        return result;
    }
};

void runTransportConfigTests() {
    TestRunner::run("Config Parsing - Separate Clock and Transport Devices", []() {
        std::string configJson = "{\"midiDevicesToSendClockTo\": [\"Device1\", \"Device2\"], \"midiDevicesToSendTransportTo\": [\"Device1\", \"Device3\"]}";
        
        MockBackendSettings settings;
        if (!settings.loadFromString(configJson)) {
            return TestResult{false, "Failed to parse config JSON"};
        }
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        if (clockDevices.size() != 2 || clockDevices[0] != "Device1" || clockDevices[1] != "Device2") {
            return TestResult{false, "Clock devices not parsed correctly"};
        }
        
        if (transportDevices.size() != 2 || transportDevices[0] != "Device1" || transportDevices[1] != "Device3") {
            return TestResult{false, "Transport devices not parsed correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Config Parsing - Empty Arrays", []() {
        std::string configJson = R"({
            "midiDevicesToSendClockTo": [],
            "midiDevicesToSendTransportTo": [],
            "pushClockDeviceName": ""
        })";
        
        MockBackendSettings settings;
        settings.loadFromString(configJson);
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        if (!clockDevices.empty()) {
            return TestResult{false, "Empty clock devices array not handled correctly"};
        }
        
        if (!transportDevices.empty()) {
            return TestResult{false, "Empty transport devices array not handled correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Config Parsing - Missing Transport Config (Backward Compatibility)", []() {
        std::string configJson = R"({
            "midiDevicesToSendClockTo": ["Device1", "Device2"],
            "pushClockDeviceName": "Ableton Push 2 Live Port"
        })";
        
        MockBackendSettings settings;
        settings.loadFromString(configJson);
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        if (clockDevices.size() != 2) {
            return TestResult{false, "Clock devices not parsed when transport config missing"};
        }
        
        if (!transportDevices.empty()) {
            return TestResult{false, "Transport devices should be empty when not configured"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Config Parsing - Single Device Arrays", []() {
        std::string configJson = R"({
            "midiDevicesToSendClockTo": ["OnlyClockDevice"],
            "midiDevicesToSendTransportTo": ["OnlyTransportDevice"]
        })";
        
        MockBackendSettings settings;
        settings.loadFromString(configJson);
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        if (clockDevices.size() != 1 || clockDevices[0] != "OnlyClockDevice") {
            return TestResult{false, "Single clock device not parsed correctly"};
        }
        
        if (transportDevices.size() != 1 || transportDevices[0] != "OnlyTransportDevice") {
            return TestResult{false, "Single transport device not parsed correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Config Validation - Device Name Overlap", []() {
        std::string configJson = R"({
            "midiDevicesToSendClockTo": ["SharedDevice", "ClockOnly"],
            "midiDevicesToSendTransportTo": ["SharedDevice", "TransportOnly"]
        })";
        
        MockBackendSettings settings;
        settings.loadFromString(configJson);
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        // Verify SharedDevice appears in both lists
        bool sharedInClock = false, sharedInTransport = false;
        for (const auto& device : clockDevices) {
            if (device == "SharedDevice") sharedInClock = true;
        }
        for (const auto& device : transportDevices) {
            if (device == "SharedDevice") sharedInTransport = true;
        }
        
        if (!sharedInClock || !sharedInTransport) {
            return TestResult{false, "Shared device not found in both lists"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("Config Edge Cases - Special Characters in Device Names", []() {
        std::string configJson = "{\"midiDevicesToSendClockTo\": [\"Device-1\", \"Device_2\", \"Device (3)\"], \"midiDevicesToSendTransportTo\": [\"Device-1\", \"Device with spaces\"]}";
        
        MockBackendSettings settings;
        settings.loadFromString(configJson);
        
        auto clockDevices = settings.getClockDevices();
        auto transportDevices = settings.getTransportDevices();
        
        if (clockDevices.size() != 3) {
            return TestResult{false, "Special character device names not parsed correctly"};
        }
        
        // Check specific device names with special characters
        bool foundDash = false, foundUnderscore = false, foundParens = false;
        for (const auto& device : clockDevices) {
            if (device == "Device-1") foundDash = true;
            if (device == "Device_2") foundUnderscore = true;
            if (device == "Device (3)") foundParens = true;
        }
        
        if (!foundDash || !foundUnderscore || !foundParens) {
            return TestResult{false, "Special character device names not preserved"};
        }
        
        return TestResult{true, ""};
    });
}

int main() {
    std::cout << "Shepherd Transport Configuration Tests" << std::endl;
    std::cout << "======================================" << std::endl;
    
    runTransportConfigTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}