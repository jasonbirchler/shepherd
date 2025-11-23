# pyshepherd - Shepherd MIDI Sequencer Backend
# Dual-purpose: Direct Python API and WebSocket client compatibility

# Direct backend API
from .backend import (
    Sequencer,
    Session, 
    Track,
    Clip,
    SequenceEvent,
    MusicalContext,
    HardwareDevice,
    HardwareDeviceManager
)

# WebSocket client API (compatibility)
from .client import ShepherdBackendControllerApp

__version__ = "2.0.0"

__all__ = [
    # Direct backend API
    'Sequencer',
    'Session',
    'Track', 
    'Clip',
    'SequenceEvent',
    'MusicalContext',
    'HardwareDevice',
    'HardwareDeviceManager',
    
    # WebSocket client API
    'ShepherdBackendControllerApp'
]
