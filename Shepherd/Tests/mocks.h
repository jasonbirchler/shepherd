#pragma once
#include <vector>
#include <string>
#include <functional>
#include <map>

// Mock MIDI Message
struct MockMidiMessage {
    int channel = 1;
    int note = 60;
    int velocity = 127;
    double timestamp = 0.0;
    std::vector<uint8_t> rawData;
    
    MockMidiMessage(int ch = 1, int n = 60, int vel = 127) 
        : channel(ch), note(n), velocity(vel) {}
};

// Mock MIDI Device Data
struct MockMidiDeviceData {
    std::string name;
    bool isOpen = false;
    std::vector<MockMidiMessage> sentMessages;
    std::vector<MockMidiMessage> receivedMessages;
    
    MockMidiDeviceData(const std::string& deviceName) : name(deviceName) {}
    
    void sendMessage(const MockMidiMessage& msg) {
        sentMessages.push_back(msg);
    }
    
    void receiveMessage(const MockMidiMessage& msg) {
        receivedMessages.push_back(msg);
    }
};

// Mock MIDI Device Manager
class MockMidiDeviceManager {
public:
    std::map<std::string, MockMidiDeviceData*> outputDevices;
    std::map<std::string, MockMidiDeviceData*> inputDevices;
    
    MockMidiDeviceData* getOutputDevice(const std::string& name) {
        auto it = outputDevices.find(name);
        return it != outputDevices.end() ? it->second : nullptr;
    }
    
    MockMidiDeviceData* getInputDevice(const std::string& name) {
        auto it = inputDevices.find(name);
        return it != inputDevices.end() ? it->second : nullptr;
    }
    
    void addOutputDevice(const std::string& name) {
        outputDevices[name] = new MockMidiDeviceData(name);
    }
    
    void addInputDevice(const std::string& name) {
        inputDevices[name] = new MockMidiDeviceData(name);
    }
    
    ~MockMidiDeviceManager() {
        for (auto& pair : outputDevices) delete pair.second;
        for (auto& pair : inputDevices) delete pair.second;
    }
};

// Mock WebSocket Message
struct MockWebSocketMessage {
    std::string address;
    std::string data;
    double timestamp = 0.0;
    
    MockWebSocketMessage(const std::string& addr, const std::string& payload) 
        : address(addr), data(payload) {}
};

// Mock WebSocket Connection
class MockWebSocketConnection {
public:
    std::vector<MockWebSocketMessage> sentMessages;
    std::vector<MockWebSocketMessage> receivedMessages;
    bool isConnected = false;
    std::function<void(const MockWebSocketMessage&)> messageHandler;
    
    void connect() { isConnected = true; }
    void disconnect() { isConnected = false; }
    
    void send(const std::string& address, const std::string& data) {
        if (isConnected) {
            sentMessages.emplace_back(address, data);
        }
    }
    
    void simulateReceive(const std::string& address, const std::string& data) {
        if (isConnected && messageHandler) {
            MockWebSocketMessage msg(address, data);
            receivedMessages.push_back(msg);
            messageHandler(msg);
        }
    }
    
    void setMessageHandler(std::function<void(const MockWebSocketMessage&)> handler) {
        messageHandler = handler;
    }
};

// Mock Global Settings
struct MockGlobalSettings {
    double sampleRate = 44100.0;
    int samplesPerSlice = 512;
    
    static MockGlobalSettings& getInstance() {
        static MockGlobalSettings instance;
        return instance;
    }
};

// Mock Timer for deterministic timing tests
class MockTimer {
public:
    double currentTime = 0.0;
    
    void advance(double seconds) {
        currentTime += seconds;
    }
    
    double getCurrentTime() const {
        return currentTime;
    }
    
    void reset() {
        currentTime = 0.0;
    }
};