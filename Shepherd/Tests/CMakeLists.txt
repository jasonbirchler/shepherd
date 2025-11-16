cmake_minimum_required(VERSION 3.15)

project(ShepherdTests)

# Find required packages
find_package(PkgConfig REQUIRED)

# Add JUCE
add_subdirectory(../3rdParty/JUCE JUCE)

# Test executable
add_executable(ShepherdTests
    test_main.cpp
    test_musical_context.cpp
    test_hardware_device.cpp
)

# Include directories
target_include_directories(ShepherdTests PRIVATE
    ../Source
    ../Source/common
    ../3rdParty/JUCE/modules
)

# Link libraries
target_link_libraries(ShepherdTests PRIVATE
    juce::juce_core
    juce::juce_audio_basics
    juce::juce_audio_devices
    juce::juce_data_structures
    juce::juce_events
)

# Compile definitions
target_compile_definitions(ShepherdTests PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_APPLICATION_NAME_STRING="ShepherdTests"
    JUCE_APPLICATION_VERSION_STRING="1.0.0"
)

# C++ standard
set_target_properties(ShepherdTests PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)