import uuid
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from .clip import Clip

if TYPE_CHECKING:
    from .session import Session


class Track:
    """Represents a MIDI track with clips and hardware device routing"""
    
    def __init__(self, name: str, num_scenes: int, session: 'Session'):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.session = session
        
        # Hardware routing
        self.output_hardware_device_name = ""
        self.input_monitoring = False
        
        # Create clips for each scene
        self.clips: List[Clip] = []
        for i in range(num_scenes):
            clip = Clip(
                name=f"{name} Clip {i+1}",
                track=self
            )
            self.clips.append(clip)
    
    def process_slice(self, slice_range: Tuple[float, float]):
        """Process MIDI for this track during a slice"""
        # Process all clips
        for clip in self.clips:
            if clip.is_playing:
                clip.process_slice(slice_range)
    
    def set_output_device(self, device_name: str):
        """Set the output hardware device"""
        self.output_hardware_device_name = device_name
    
    def get_output_device(self):
        """Get the output hardware device"""
        if self.output_hardware_device_name:
            return self.session.sequencer.hardware_devices.get_output_device(
                self.output_hardware_device_name
            )
        return None
    
    def send_midi_message(self, message):
        """Send MIDI message through this track's output device"""
        device = self.get_output_device()
        if device:
            device.send_message(message)
    
    def get_clip(self, scene_idx: int) -> Optional[Clip]:
        """Get clip by scene index"""
        if 0 <= scene_idx < len(self.clips):
            return self.clips[scene_idx]
        return None
    
    def play_clip(self, scene_idx: int):
        """Play a specific clip"""
        clip = self.get_clip(scene_idx)
        if clip:
            # Stop other clips in this track first
            for other_clip in self.clips:
                if other_clip != clip and other_clip.is_playing:
                    other_clip.stop()
            clip.play()
    
    def stop_all_clips(self):
        """Stop all clips in this track"""
        for clip in self.clips:
            clip.stop()
    
    def set_input_monitoring(self, enabled: bool):
        """Enable/disable input monitoring"""
        self.input_monitoring = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'output_hardware_device_name': self.output_hardware_device_name,
            'input_monitoring': self.input_monitoring,
            'clips': [clip.to_dict() for clip in self.clips]
        }