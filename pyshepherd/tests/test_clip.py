import pytest
from unittest.mock import Mock, patch
from pyshepherd.backend import Clip, SequenceEvent


class TestSequenceEvent:
    """Test suite for SequenceEvent"""
    
    def test_sequence_event_creation(self):
        """Test sequence event creation"""
        event = SequenceEvent(
            timestamp=1.0,
            note=60,
            velocity=100,
            duration=0.5,
            channel=2
        )
        
        assert event.timestamp == 1.0
        assert event.note == 60
        assert event.velocity == 100
        assert event.duration == 0.5
        assert event.channel == 2
        assert event.chance == 1.0
        assert event.uuid is not None
    
    def test_sequence_event_serialization(self):
        """Test sequence event to_dict conversion"""
        event = SequenceEvent(1.5, 64, 127, 0.25, 3)
        
        data = event.to_dict()
        
        assert data['timestamp'] == 1.5
        assert data['note'] == 64
        assert data['velocity'] == 127
        assert data['duration'] == 0.25
        assert data['channel'] == 3
        assert data['chance'] == 1.0
        assert 'uuid' in data


class TestClip:
    """Test suite for Clip functionality"""
    
    def test_clip_creation(self):
        """Test clip creation with default settings"""
        track = Mock()
        
        clip = Clip("Test Clip", track)
        
        assert clip.name == "Test Clip"
        assert clip.track == track
        assert clip.is_playing == False
        assert clip.is_recording == False
        assert clip.length_beats == 4.0
        assert clip.bpm_multiplier == 1.0
        assert clip.quantization_step == 0.25
        assert clip.wrap_events_across_loop == True
        assert len(clip.sequence_events) == 0
    
    def test_clip_playback_control(self):
        """Test clip play/stop functionality"""
        track = Mock()
        clip = Clip("Test Clip", track)
        
        # Test play
        clip.play()
        assert clip.is_playing == True
        assert clip.playhead_position_beats == 0.0
        
        # Test stop
        clip.stop()
        assert clip.is_playing == False
        assert clip.playhead_position_beats == 0.0
        
        # Test toggle
        clip.toggle_play_stop()
        assert clip.is_playing == True
        
        clip.toggle_play_stop()
        assert clip.is_playing == False
    
    def test_clip_recording_control(self):
        """Test clip recording functionality"""
        track = Mock()
        clip = Clip("Test Clip", track)
        
        # Start recording
        clip.start_recording()
        assert clip.is_recording == True
        assert clip.is_playing == True  # Should auto-start playback
        
        # Stop recording
        clip.stop_recording()
        assert clip.is_recording == False
    
    def test_clip_sequence_event_management(self):
        """Test adding and removing sequence events"""
        track = Mock()
        clip = Clip("Test Clip", track)
        
        # Add note event
        event = clip.add_note_event(1.0, 60, 100, 0.5, 1)
        
        assert len(clip.sequence_events) == 1
        assert clip.sequence_events[0] == event
        assert event.timestamp == 1.0
        assert event.note == 60
        
        # Remove event
        clip.remove_event(event.uuid)
        assert len(clip.sequence_events) == 0
        
        # Clear all events
        clip.add_note_event(0.0, 60, 100, 0.5)
        clip.add_note_event(1.0, 64, 100, 0.5)
        assert len(clip.sequence_events) == 2
        
        clip.clear_sequence()
        assert len(clip.sequence_events) == 0
    
    def test_clip_length_management(self):
        """Test clip length setting"""
        track = Mock()
        clip = Clip("Test Clip", track)
        
        # Set valid length
        clip.set_length(8.0)
        assert clip.length_beats == 8.0
        
        # Invalid length should be ignored
        clip.set_length(-1.0)
        assert clip.length_beats == 8.0
        
        clip.set_length(0.0)
        assert clip.length_beats == 8.0
    
    def test_clip_quantization(self):
        """Test event quantization"""
        track = Mock()
        clip = Clip("Test Clip", track)
        
        # Add events with unquantized timing
        clip.add_note_event(1.1, 60, 100, 0.5)
        clip.add_note_event(2.3, 64, 100, 0.5)
        
        # Quantize to quarter notes
        clip.quantize_events(1.0)
        
        assert clip.sequence_events[0].timestamp == 1.0
        assert clip.sequence_events[1].timestamp == 2.0
        assert clip.quantization_step == 1.0
    
    @patch('random.random')
    def test_clip_process_slice_basic(self, mock_random):
        """Test basic slice processing"""
        mock_random.return_value = 0.5  # Always trigger events
        
        track = Mock()
        track.send_midi_message = Mock()
        
        clip = Clip("Test Clip", track)
        clip.add_note_event(0.5, 60, 100, 0.25)
        clip.play()
        
        # Process slice that includes the event
        clip.process_slice((0.0, 1.0))
        
        # Should send MIDI messages
        assert track.send_midi_message.call_count == 2  # Note on + note off
    
    def test_clip_process_slice_playhead_advance(self):
        """Test playhead advancement during slice processing"""
        track = Mock()
        clip = Clip("Test Clip", track)
        clip.play()
        
        # Process slice
        clip.process_slice((0.0, 0.5))
        assert clip.playhead_position_beats == 0.5
        
        # Process another slice
        clip.process_slice((0.5, 1.0))
        assert clip.playhead_position_beats == 1.0
    
    def test_clip_looping_behavior(self):
        """Test clip looping when reaching end"""
        track = Mock()
        clip = Clip("Test Clip", track)
        clip.set_length(2.0)
        clip.play()
        
        # Process slice that goes beyond clip length
        clip.playhead_position_beats = 1.5
        clip.process_slice((1.5, 2.5))  # 1.0 beat slice
        
        # Should wrap around
        assert clip.playhead_position_beats == 0.5
        assert clip.is_playing == True
    
    def test_clip_no_looping_behavior(self):
        """Test clip stopping when looping disabled"""
        track = Mock()
        clip = Clip("Test Clip", track)
        clip.set_length(2.0)
        clip.wrap_events_across_loop = False
        clip.play()
        
        # Process slice that goes beyond clip length
        clip.playhead_position_beats = 1.5
        clip.process_slice((1.5, 2.5))
        
        # Should stop playing
        assert clip.is_playing == False
    
    @patch('random.random')
    def test_clip_event_chance(self, mock_random):
        """Test event chance/probability"""
        track = Mock()
        track.send_midi_message = Mock()
        
        clip = Clip("Test Clip", track)
        event = clip.add_note_event(0.5, 60, 100, 0.25)
        event.chance = 0.5  # 50% chance
        clip.play()
        
        # Event should not trigger
        mock_random.return_value = 0.8  # > 0.5
        clip.process_slice((0.0, 1.0))
        track.send_midi_message.assert_not_called()
        
        # Event should trigger
        mock_random.return_value = 0.3  # < 0.5
        clip.process_slice((0.0, 1.0))
        assert track.send_midi_message.call_count == 2  # Note on + off
    
    def test_clip_serialization(self):
        """Test clip to_dict conversion"""
        track = Mock()
        clip = Clip("Test Clip", track)
        clip.set_length(8.0)
        clip.add_note_event(1.0, 60, 100, 0.5)
        clip.play()
        
        data = clip.to_dict()
        
        assert data['name'] == "Test Clip"
        assert data['is_playing'] == True
        assert data['length_beats'] == 8.0
        assert len(data['sequence_events']) == 1
        assert 'uuid' in data