CXX = g++
CXXFLAGS = -std=c++17 -I../Source -I../Source/common -I../JuceLibraryCode -I../3rdParty/JUCE/modules -DNDEBUG=1
LDFLAGS = -framework CoreFoundation -framework CoreAudio -framework CoreMidi -framework AudioToolbox -framework Accelerate

# Source files
SOURCES = test_main.cpp test_musical_context.cpp test_hardware_device.cpp
SHEPHERD_SOURCES = ../Source/MusicalContext.cpp ../Source/HardwareDevice.cpp

# JUCE library code
JUCE_SOURCES = ../JuceLibraryCode/include_juce_core.cpp \
               ../JuceLibraryCode/include_juce_data_structures.cpp \
               ../JuceLibraryCode/include_juce_events.cpp \
               ../JuceLibraryCode/include_juce_audio_basics.cpp

TARGET = ShepherdTests

all: $(TARGET)

$(TARGET): $(SOURCES) $(SHEPHERD_SOURCES) $(JUCE_SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(SHEPHERD_SOURCES) $(JUCE_SOURCES) $(LDFLAGS)

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all test clean