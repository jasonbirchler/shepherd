#include "../JuceLibraryCode/JuceHeader.h"
#include "MusicalContext.h"
#include "helpers_shepherd.h"

extern void TestRunner::run(const juce::String&, std::function<TestResult()>);

// Mock global settings
GlobalSettingsStruct mockGlobalSettings() {
    GlobalSettingsStruct settings;
    settings.sampleRate = 44100.0;
    settings.samplesPerSlice = 512;
    return settings;
}

void runMusicalContextTests() {
    TestRunner::run("MusicalContext - Constructor", []() {
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
    
    TestRunner::run("MusicalContext - BPM Setting", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setBpm(140.0);
        if (context.getBpm() != 140.0) {
            return TestResult{false, "BPM not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Meter Setting", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setMeter(3);
        if (context.getMeter() != 3) {
            return TestResult{false, "Meter not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Playhead Position", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setPlayheadPosition(4.5);
        if (context.getPlayheadPositionInBeats() != 4.5) {
            return TestResult{false, "Playhead position not set correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Playing State", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        context.setPlayheadIsPlaying(true);
        if (!context.playheadIsPlaying()) {
            return TestResult{false, "Playing state not set correctly"};
        }
        
        context.setPlayheadIsPlaying(false);
        if (context.playheadIsPlaying()) {
            return TestResult{false, "Playing state not cleared correctly"};
        }
        return TestResult{true, ""};
    });
    
    TestRunner::run("MusicalContext - Metronome Toggle", []() {
        juce::ValueTree state(ShepherdIDs::MUSICAL_CONTEXT);
        MusicalContext context(mockGlobalSettings, state);
        
        bool initialState = context.metronomeIsOn();
        context.toggleMetronome();
        if (context.metronomeIsOn() == initialState) {
            return TestResult{false, "Metronome toggle not working"};
        }
        return TestResult{true, ""};
    });
}