#include "../JuceLibraryCode/JuceHeader.h"
#include <iostream>

// Simple test framework
struct TestResult {
    bool passed = true;
    juce::String message;
};

class TestRunner {
public:
    static void run(const juce::String& testName, std::function<TestResult()> test) {
        std::cout << "Running " << testName.toStdString() << "... ";
        auto result = test();
        if (result.passed) {
            std::cout << "PASS" << std::endl;
            passCount++;
        } else {
            std::cout << "FAIL: " << result.message.toStdString() << std::endl;
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

// Test declarations
void runJuceBasicTests();
void runMusicalContextTests();

int main() {
    std::cout << "Shepherd JUCE-based Tests" << std::endl;
    std::cout << "=========================" << std::endl;
    
    runJuceBasicTests();
    runMusicalContextTests();
    
    TestRunner::printSummary();
    return TestRunner::getFailCount() > 0 ? 1 : 0;
}