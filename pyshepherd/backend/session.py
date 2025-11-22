import uuid
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .track import Track

if TYPE_CHECKING:
    from .sequencer import Sequencer


class Session:
    """Represents a Shepherd session with tracks and scenes"""
    
    def __init__(self, name: str, num_tracks: int, num_scenes: int, sequencer: 'Sequencer'):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.num_tracks = num_tracks
        self.num_scenes = num_scenes
        self.sequencer = sequencer
        
        # Session settings
        self.fixed_length_recording_bars = 0
        self.record_automation_enabled = False
        self.fixed_velocity = 100
        
        # Create tracks
        self.tracks: List[Track] = []
        for i in range(num_tracks):
            track = Track(
                name=f"Track {i+1}",
                num_scenes=num_scenes,
                session=self
            )
            self.tracks.append(track)
    
    def play(self):
        """Start playback"""
        self.sequencer.musical_context.set_playing(True)
    
    def stop(self):
        """Stop playback"""
        self.sequencer.musical_context.set_playing(False)
    
    def play_stop_toggle(self):
        """Toggle play/stop"""
        is_playing = self.sequencer.musical_context.is_playing
        self.sequencer.musical_context.set_playing(not is_playing)
    
    def play_scene(self, scene_idx: int):
        """Play all clips in a scene"""
        if 0 <= scene_idx < self.num_scenes:
            for track in self.tracks:
                if scene_idx < len(track.clips):
                    track.clips[scene_idx].play()
    
    def stop_all_clips(self):
        """Stop all playing clips"""
        for track in self.tracks:
            for clip in track.clips:
                clip.stop()
    
    def set_bpm(self, bpm: float):
        """Set session BPM"""
        self.sequencer.musical_context.set_bpm(bpm)
    
    def set_meter(self, meter: int):
        """Set session meter"""
        self.sequencer.musical_context.set_meter(meter)
    
    def set_metronome(self, enabled: bool):
        """Enable/disable metronome"""
        self.sequencer.musical_context.set_metronome(enabled)
    
    def get_track(self, track_idx: int) -> Optional[Track]:
        """Get track by index"""
        if 0 <= track_idx < len(self.tracks):
            return self.tracks[track_idx]
        return None
    
    def save(self, filepath: str):
        """Save session to file"""
        # TODO: Implement session serialization
        pass
    
    def load(self, filepath: str):
        """Load session from file"""
        # TODO: Implement session deserialization
        pass
    
    @property
    def is_playing(self) -> bool:
        """Check if session is playing"""
        return self.sequencer.musical_context.is_playing
    
    @property
    def bpm(self) -> float:
        """Get current BPM"""
        return self.sequencer.musical_context.bpm
    
    @property
    def meter(self) -> int:
        """Get current meter"""
        return self.sequencer.musical_context.meter
    
    @property
    def metronome_on(self) -> bool:
        """Check if metronome is enabled"""
        return self.sequencer.musical_context.metronome_on
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'num_tracks': self.num_tracks,
            'num_scenes': self.num_scenes,
            'fixed_length_recording_bars': self.fixed_length_recording_bars,
            'record_automation_enabled': self.record_automation_enabled,
            'fixed_velocity': self.fixed_velocity,
            'tracks': [track.to_dict() for track in self.tracks],
            'is_playing': self.is_playing,
            'bpm': self.bpm,
            'meter': self.meter,
            'metronome_on': self.metronome_on
        }