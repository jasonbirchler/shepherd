# pyshepherd - Shepherd MIDI Sequencer Backend
# Dual-purpose: Direct Python API and WebSocket client compatibility

# Direct backend API (new)
from .backend import (
    Sequencer,
    Session, 
    Track,
    Clip,
    MusicalContext,
    HardwareDevice,
    HardwareDeviceManager
)

# WebSocket client API (existing compatibility)
from .pyshepherd import (
    ShepherdBackendControllerApp,
    State,
    Session as ClientSession,
    Track as ClientTrack, 
    Clip as ClientClip,
    HardwareDevice as ClientHardwareDevice,
    SequenceEvent
)

__version__ = "2.0.0"

__all__ = [
    # Direct backend API
    'Sequencer',
    'Session',
    'Track', 
    'Clip',
    'MusicalContext',
    'HardwareDevice',
    'HardwareDeviceManager',
    
    # WebSocket client API (compatibility)
    'ShepherdBackendControllerApp',
    'State',
    'ClientSession',
    'ClientTrack',
    'ClientClip', 
    'ClientHardwareDevice',
    'SequenceEvent'
]