# Compatibility shim for existing Push2Controller
# This maintains the old import path while using the new client

from .client import ShepherdBackendControllerApp

# Import real backend classes
from .backend.session import Session as RealSession
from .backend.track import Track as RealTrack  
from .backend.clip import Clip as RealClip

# For compatibility - application will use real classes when backend is connected
# Mock classes are used as fallback when backend is unavailable

# Mock classes for compatibility
class SequenceEvent:
    """Mock SequenceEvent for compatibility"""
    def __init__(self):
        self.uuid = ""
        self.timestamp = 0.0
        self.note = 60
        self.velocity = 100
        self.duration = 0.5
        self.channel = 1

class HardwareDevice:
    """Mock HardwareDevice for compatibility"""
    def __init__(self):
        self.uuid = ""
        self.name = ""
        self.short_name = ""
        self.type = 0
        self.midi_channel = 1
    
    def is_type_output(self):
        return self.type == 1
    
    def is_type_input(self):
        return self.type == 0

# Re-export for compatibility - the real backend classes
__all__ = [
    'ShepherdBackendControllerApp',
    'RealSession',
    'RealTrack', 
    'RealClip'
]

# Compatibility aliases for existing code that expects State, Session, Track, Clip
# State is the app instance itself (no separate class needed)
State = None  # State is represented by the app instance
Session = RealSession  
Track = RealTrack
Clip = RealClip
