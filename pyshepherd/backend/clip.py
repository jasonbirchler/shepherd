import uuid
import mido
from typing import List, Dict, Any, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .track import Track


class SequenceEvent:
    """Represents a MIDI event in a clip sequence"""
    
    def __init__(self, timestamp: float, note: int, velocity: int, duration: float, channel: int = 1):
        self.uuid = str(uuid.uuid4())
        self.timestamp = timestamp  # Position in beats
        self.note = note
        self.velocity = velocity
        self.duration = duration  # Length in beats
        self.channel = channel
        self.chance = 1.0  # Probability of playing (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'uuid': self.uuid,
            'timestamp': self.timestamp,
            'note': self.note,
            'velocity': self.velocity,
            'duration': self.duration,
            'channel': self.channel,
            'chance': self.chance
        }


class Clip:
    """Represents a MIDI clip with sequence events and playback state"""
    
    def __init__(self, name: str, track: 'Track'):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.track = track
        
        # Playback state
        self.is_playing = False
        self.is_recording = False
        self.playhead_position_beats = 0.0
        
        # Clip settings
        self.length_beats = 4.0  # Default 1 bar at 4/4
        self.bpm_multiplier = 1.0
        self.quantization_step = 0.25  # 16th notes
        self.wrap_events_across_loop = True
        
        # Sequence data
        self.sequence_events: List[SequenceEvent] = []
        
        # Cue points for scheduled play/stop
        self.will_play_at = -1.0
        self.will_stop_at = -1.0
        self.will_start_recording_at = -1.0
        self.will_stop_recording_at = -1.0
    
    def play(self):
        """Start playing the clip"""
        self.is_playing = True
        self.playhead_position_beats = 0.0
    
    def stop(self):
        """Stop playing the clip"""
        self.is_playing = False
        self.playhead_position_beats = 0.0
    
    def toggle_play_stop(self):
        """Toggle play/stop state"""
        if self.is_playing:
            self.stop()
        else:
            self.play()
    
    def start_recording(self):
        """Start recording into the clip"""
        self.is_recording = True
        if not self.is_playing:
            self.play()
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
    
    def process_slice(self, slice_range: Tuple[float, float]):
        """Process MIDI events for this slice"""
        if not self.is_playing:
            return
        
        start_beats, end_beats = slice_range
        slice_length = end_beats - start_beats
        
        # Update clip playhead
        self.playhead_position_beats += slice_length
        
        # Handle looping
        if self.playhead_position_beats >= self.length_beats:
            if self.wrap_events_across_loop:
                self.playhead_position_beats = self.playhead_position_beats % self.length_beats
            else:
                self.stop()
                return
        
        # Generate MIDI messages for events in this slice
        self._generate_midi_for_slice(slice_range)
    
    def _generate_midi_for_slice(self, slice_range: Tuple[float, float]):
        """Generate MIDI messages for events in the current slice"""
        start_beats, end_beats = slice_range
        
        for event in self.sequence_events:
            # Check if event starts within this slice
            event_start = event.timestamp
            event_end = event_start + event.duration
            
            # Handle looping
            if self.wrap_events_across_loop:
                if event_start >= self.length_beats:
                    continue  # Event is beyond clip length
                
                # Check if event wraps around
                if event_end > self.length_beats:
                    event_end = event_end % self.length_beats
            
            # Check if event intersects with slice
            if self._event_intersects_slice(event_start, event_end, start_beats, end_beats):
                self._send_midi_for_event(event, slice_range)
    
    def _event_intersects_slice(self, event_start: float, event_end: float, 
                               slice_start: float, slice_end: float) -> bool:
        """Check if an event intersects with the current slice"""
        return not (event_end <= slice_start or event_start >= slice_end)
    
    def _send_midi_for_event(self, event: SequenceEvent, slice_range: Tuple[float, float]):
        """Send MIDI messages for a sequence event"""
        # Apply chance/probability
        import random
        if random.random() > event.chance:
            return
        
        # Create note on message
        note_on = mido.Message('note_on',
                              channel=event.channel - 1,  # mido uses 0-15
                              note=event.note,
                              velocity=event.velocity)
        
        # Create note off message
        note_off = mido.Message('note_off',
                               channel=event.channel - 1,
                               note=event.note,
                               velocity=0)
        
        # Send through track's output device
        self.track.send_midi_message(note_on)
        
        # TODO: Schedule note off message based on duration
        # For now, send immediate note off (this needs proper timing)
        self.track.send_midi_message(note_off)
    
    def add_note_event(self, timestamp: float, note: int, velocity: int, duration: float, channel: int = 1):
        """Add a note event to the sequence"""
        event = SequenceEvent(timestamp, note, velocity, duration, channel)
        self.sequence_events.append(event)
        return event
    
    def remove_event(self, event_uuid: str):
        """Remove an event by UUID"""
        self.sequence_events = [e for e in self.sequence_events if e.uuid != event_uuid]
    
    def clear_sequence(self):
        """Clear all sequence events"""
        self.sequence_events.clear()
    
    def set_length(self, length_beats: float):
        """Set clip length in beats"""
        if length_beats > 0:
            self.length_beats = length_beats
    
    def quantize_events(self, quantization_step: float):
        """Quantize all events to the specified step"""
        self.quantization_step = quantization_step
        for event in self.sequence_events:
            event.timestamp = round(event.timestamp / quantization_step) * quantization_step
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'is_playing': self.is_playing,
            'is_recording': self.is_recording,
            'playhead_position_beats': self.playhead_position_beats,
            'length_beats': self.length_beats,
            'bpm_multiplier': self.bpm_multiplier,
            'quantization_step': self.quantization_step,
            'wrap_events_across_loop': self.wrap_events_across_loop,
            'sequence_events': [event.to_dict() for event in self.sequence_events],
            'will_play_at': self.will_play_at,
            'will_stop_at': self.will_stop_at
        }