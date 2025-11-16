#include "../JuceLibraryCode/JuceHeader.h"
#include "MusicalContext.h"
#include "helpers_shepherd.h"

// Forward declarations from main file
struct TestResult {
    bool passed = true;
    juce::String message;
};

class TestRunner {
public:
    static void run(const juce::String& testName, std::function<TestResult()> test);
};

// Mock global settings
GlobalSettingsStruct mockGlobalSettings() {
    GlobalSettingsStruct settings;
    settings.sampleRate = 44100.0;
    settings.samplesPerSlice = 512;
    return settings;
}

void runJuceBasicTests() {
    TestRunner::run("JUCE ValueTree Basic Operations", []() {
        juce::ValueTree root("ROOT");
        root.setProperty("testProp", 42, nullptr);
        
        if (!root.hasProperty("testProp")) {
            return TestResult{false, "Property not set"};
        }
        
        if ((int)root.getProperty("testProp") != 42) {
            return TestResult{false, "Property value incorrect"};
        }
        
        juce::ValueTree child("CHILD");
        child.setProperty("childProp", "test", nullptr);
        root.appendChild(child, nullptr);
        
        if (root.getNumChildren() != 1) {
            return TestResult{false, "Child not added"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("JUCE String Operations", []() {
        juce::String str1 = "Hello";
        juce::String str2 = " World";
        juce::String combined = str1 + str2;
        
        if (combined != "Hello World") {
            return TestResult{false, "String concatenation failed"};
        }
        
        if (combined.length() != 11) {
            return TestResult{false, "String length incorrect"};
        }
        
        return TestResult{true, ""};
    });
}

void runMusicalContextTests() {
    TestRunner::run("MusicalContext - Constructor with ValueTree", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        if (context.getBpm() != ShepherdDefaults::bpm) {
            return TestResult{false, "Default BPM not set correctly"};
        }
        if (context.getMeter() != ShepherdDefaults::meter) {
            return TestResult{false, "Default meter not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - BPM Management", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setBpm(140.0);
        if (context.getBpm() != 140.0) {
            return TestResult{false, "BPM not set correctly"};
        }
        
        // Test state synchronization
        context.updateStateMemberVersions();
        double stateBpm = state.getProperty(ShepherdIDs::bpm, 0.0);
        if (stateBpm != 140.0) {
            return TestResult{false, "BPM not synchronized to state"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Playhead Management", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setPlayheadPosition(4.5);
        if (context.getPlayheadPositionInBeats() != 4.5) {
            return TestResult{false, "Playhead position not set correctly"};
        }
        
        context.setPlayheadIsPlaying(true);
        if (!context.playheadIsPlaying()) {
            return TestResult{false, "Playing state not set correctly"};
        }
        
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Metronome Control", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        bool initialState = context.metronomeIsOn();
        context.toggleMetronome();
        if (context.metronomeIsOn() == initialState) {
            return TestResult{false, "Metronome toggle not working"};
        }
        
        context.setMetronome(true);
        if (!context.metronomeIsOn()) {
            return TestResult{false, "Metronome set not working"};
        }
        
        return TestResult{true, ""};
    });
}