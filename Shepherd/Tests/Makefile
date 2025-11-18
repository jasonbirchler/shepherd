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
TRANSPORT_TARGET = midi_transport_tests
CONFIG_TARGET = transport_config_tests
COMPONENT_TARGET = backend_component_tests

all: $(TARGET) $(TRANSPORT_TARGET) $(CONFIG_TARGET) $(COMPONENT_TARGET)

$(TARGET): $(SOURCES) $(SHEPHERD_SOURCES) $(JUCE_SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(SHEPHERD_SOURCES) $(JUCE_SOURCES) $(LDFLAGS)

$(TRANSPORT_TARGET): midi_transport_tests.cpp mocks.h
	$(CXX) -std=c++17 -Wall -Wextra -O2 -o $(TRANSPORT_TARGET) midi_transport_tests.cpp

$(CONFIG_TARGET): transport_config_tests.cpp
	$(CXX) -std=c++17 -Wall -Wextra -O2 -o $(CONFIG_TARGET) transport_config_tests.cpp

$(COMPONENT_TARGET): backend_component_tests.cpp mocks.h
	$(CXX) -std=c++17 -Wall -Wextra -O2 -o $(COMPONENT_TARGET) backend_component_tests.cpp

test: $(TARGET) $(TRANSPORT_TARGET) $(CONFIG_TARGET) $(COMPONENT_TARGET)
	@echo "Running JUCE-based tests..."
	./$(TARGET)
	@echo "\nRunning MIDI transport tests..."
	./$(TRANSPORT_TARGET)
	@echo "\nRunning transport config tests..."
	./$(CONFIG_TARGET)
	@echo "\nRunning backend component tests..."
	./$(COMPONENT_TARGET)

clean:
	rm -f $(TARGET) $(TRANSPORT_TARGET) $(CONFIG_TARGET) $(COMPONENT_TARGET)

.PHONY: all test clean