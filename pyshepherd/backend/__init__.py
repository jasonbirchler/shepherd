# Backend implementation - direct Python API
from .sequencer import Sequencer
from .session import Session
from .track import Track
from .clip import Clip, SequenceEvent
from .musical_context import MusicalContext
from .hardware_device import HardwareDevice, HardwareDeviceManager

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