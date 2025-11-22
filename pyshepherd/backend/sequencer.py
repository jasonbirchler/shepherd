import asyncio
import threading
import time
from typing import Optional, List, Dict, Any
import mido
from .session import Session
from .musical_context import MusicalContext
from .hardware_device import HardwareDeviceManager


class Sequencer:
    """Core sequencer backend - handles MIDI processing and session management"""
    
    def __init__(self, enable_websocket: bool = True, websocket_port: int = 9001):
        self.enable_websocket = enable_websocket
        self.websocket_port = websocket_port
        
        # Core components
        self.session: Optional[Session] = None
        self.musical_context = MusicalContext()
        self.hardware_devices = HardwareDeviceManager()
        
        # MIDI processing
        self.sample_rate = 44100.0
        self.samples_per_slice = 512
        self.is_running = False
        self._processing_thread: Optional[threading.Thread] = None
        
        # WebSocket server
        self._websocket_server = None
        if enable_websocket:
            self._start_websocket_server()
    
    def prepare(self, sample_rate: float = 44100.0, samples_per_slice: int = 512):
        """Initialize sequencer with audio settings"""
        self.sample_rate = sample_rate
        self.samples_per_slice = samples_per_slice
        self.musical_context.set_sample_rate(sample_rate)
        self.hardware_devices.initialize()
    
    def start(self):
        """Start the sequencer processing"""
        if self.is_running:
            return
            
        self.is_running = True
        self._processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._processing_thread.start()
    
    def stop(self):
        """Stop the sequencer processing"""
        self.is_running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=1.0)
    
    def _processing_loop(self):
        """Main processing loop - runs in separate thread"""
        slice_duration = self.samples_per_slice / self.sample_rate
        
        while self.is_running:
            start_time = time.time()
            
            # Process MIDI slice
            self._process_midi_slice()
            
            # Sleep for remaining slice time
            elapsed = time.time() - start_time
            sleep_time = max(0, slice_duration - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _process_midi_slice(self):
        """Process one slice of MIDI data"""
        if not self.session:
            return
            
        # Update musical context
        slice_range = self.musical_context.get_current_slice_range(self.samples_per_slice)
        
        # Process each track
        for track in self.session.tracks:
            track.process_slice(slice_range)
    
    def new_session(self, num_tracks: int, num_scenes: int, name: str = "New Session"):
        """Create a new session"""
        self.session = Session(
            name=name,
            num_tracks=num_tracks,
            num_scenes=num_scenes,
            sequencer=self
        )
        return self.session
    
    def load_session(self, filepath: str):
        """Load session from file"""
        # TODO: Implement session loading
        pass
    
    def save_session(self, filepath: str):
        """Save current session to file"""
        if self.session:
            self.session.save(filepath)
    
    def _start_websocket_server(self):
        """Start WebSocket server for remote control"""
        from ..server.websocket_server import WebSocketServer
        self._websocket_server = WebSocketServer(self, port=self.websocket_port)
        self._websocket_server.start()
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary for WebSocket clients"""
        return {
            'session': self.session.to_dict() if self.session else None,
            'musical_context': self.musical_context.to_dict(),
            'hardware_devices': self.hardware_devices.to_dict()
        }