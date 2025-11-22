# pyshepherd - Shepherd MIDI Sequencer Backend
# Direct Python API for MIDI sequencing

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

__version__ = "2.0.0"

__all__ = [
    'Sequencer',
    'Session',
    'Track', 
    'Clip',
    'SequenceEvent',
    'MusicalContext',
    'HardwareDevice',
    'HardwareDeviceManager'
]