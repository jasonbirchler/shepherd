# Compatibility shim for existing Push2Controller
# This maintains the old import path while using the new client

from .client import ShepherdBackendControllerApp

# Import real backend classes
from .backend.session import Session
from .backend.track import Track
from .backend.clip import Clip, SequenceEvent

# Type alias for State - the app instance itself represents the state
State = ShepherdBackendControllerApp

# Re-export for compatibility
__all__ = [
    'ShepherdBackendControllerApp',
    'State',
    'Session',
    'Track',
    'Clip',
    'SequenceEvent'
]
