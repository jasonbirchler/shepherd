import time
from typing import Tuple, Dict, Any


class MusicalContext:
    """Manages musical timing, BPM, meter, and playhead position"""
    
    def __init__(self):
        # Musical settings
        self.bpm = 120.0
        self.meter = 4
        self.metronome_on = False
        
        # Playhead state
        self.playhead_position_beats = 0.0
        self.is_playing = False
        self.doing_count_in = False
        self.count_in_position_beats = 0.0
        
        # Timing
        self.sample_rate = 44100.0
        self.bar_count = 0
        self.last_update_time = time.time()
    
    def set_sample_rate(self, sample_rate: float):
        """Set the audio sample rate"""
        self.sample_rate = sample_rate
    
    def set_bpm(self, bpm: float):
        """Set the BPM"""
        if bpm > 0:
            self.bpm = bpm
    
    def set_meter(self, meter: int):
        """Set the time signature meter"""
        if meter > 0:
            self.meter = meter
    
    def set_playing(self, playing: bool):
        """Set play/stop state"""
        self.is_playing = playing
        if playing:
            self.last_update_time = time.time()
    
    def set_metronome(self, enabled: bool):
        """Enable/disable metronome"""
        self.metronome_on = enabled
    
    def get_current_slice_range(self, samples_per_slice: int) -> Tuple[float, float]:
        """Get the beat range for the current processing slice"""
        current_time = time.time()
        
        if self.is_playing:
            # Calculate elapsed time and convert to beats
            elapsed_seconds = current_time - self.last_update_time
            elapsed_beats = elapsed_seconds * (self.bpm / 60.0)
            
            # Update playhead position
            start_position = self.playhead_position_beats
            self.playhead_position_beats += elapsed_beats
            end_position = self.playhead_position_beats
            
            self.last_update_time = current_time
            return (start_position, end_position)
        else:
            # Not playing - return current position
            return (self.playhead_position_beats, self.playhead_position_beats)
    
    def get_slice_length_beats(self, samples_per_slice: int) -> float:
        """Calculate slice length in beats"""
        slice_seconds = samples_per_slice / self.sample_rate
        return slice_seconds * (self.bpm / 60.0)
    
    def beats_to_samples(self, beats: float) -> int:
        """Convert beats to sample count"""
        seconds = beats * (60.0 / self.bpm)
        return int(seconds * self.sample_rate)
    
    def samples_to_beats(self, samples: int) -> float:
        """Convert sample count to beats"""
        seconds = samples / self.sample_rate
        return seconds * (self.bpm / 60.0)
    
    def get_next_quantized_bar_position(self) -> float:
        """Get the next bar boundary position"""
        beats_per_bar = self.meter
        current_bar = int(self.playhead_position_beats / beats_per_bar)
        return (current_bar + 1) * beats_per_bar
    
    def reset_playhead(self):
        """Reset playhead to beginning"""
        self.playhead_position_beats = 0.0
        self.bar_count = 0
        self.last_update_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'bpm': self.bpm,
            'meter': self.meter,
            'metronome_on': self.metronome_on,
            'playhead_position_beats': self.playhead_position_beats,
            'is_playing': self.is_playing,
            'doing_count_in': self.doing_count_in,
            'bar_count': self.bar_count
        }