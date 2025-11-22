import pytest
import time
from unittest.mock import patch
from pyshepherd.backend import MusicalContext


class TestMusicalContext:
    """Test suite for MusicalContext functionality"""
    
    def test_musical_context_initialization(self):
        """Test musical context creation with defaults"""
        context = MusicalContext()
        
        assert context.bpm == 120.0
        assert context.meter == 4
        assert context.metronome_on == False
        assert context.playhead_position_beats == 0.0
        assert context.is_playing == False
        assert context.doing_count_in == False
        assert context.sample_rate == 44100.0
        assert context.bar_count == 0
    
    def test_bpm_setting(self):
        """Test BPM setting and validation"""
        context = MusicalContext()
        
        # Valid BPM
        context.set_bpm(140.0)
        assert context.bpm == 140.0
        
        # Invalid BPM should be ignored
        context.set_bpm(-10.0)
        assert context.bpm == 140.0
        
        context.set_bpm(0.0)
        assert context.bpm == 140.0
    
    def test_meter_setting(self):
        """Test meter setting and validation"""
        context = MusicalContext()
        
        # Valid meter
        context.set_meter(3)
        assert context.meter == 3
        
        # Invalid meter should be ignored
        context.set_meter(-1)
        assert context.meter == 3
        
        context.set_meter(0)
        assert context.meter == 3
    
    def test_playback_control(self):
        """Test play/stop functionality"""
        context = MusicalContext()
        
        # Start playing
        context.set_playing(True)
        assert context.is_playing == True
        
        # Stop playing
        context.set_playing(False)
        assert context.is_playing == False
    
    def test_metronome_control(self):
        """Test metronome enable/disable"""
        context = MusicalContext()
        
        # Enable metronome
        context.set_metronome(True)
        assert context.metronome_on == True
        
        # Disable metronome
        context.set_metronome(False)
        assert context.metronome_on == False
    
    def test_sample_rate_setting(self):
        """Test sample rate configuration"""
        context = MusicalContext()
        
        context.set_sample_rate(48000.0)
        assert context.sample_rate == 48000.0
    
    @patch('time.time')
    def test_slice_range_calculation_stopped(self, mock_time):
        """Test slice range when not playing"""
        mock_time.return_value = 1000.0
        
        context = MusicalContext()
        context.playhead_position_beats = 2.5
        
        # When not playing, should return current position
        start, end = context.get_current_slice_range(512)
        
        assert start == 2.5
        assert end == 2.5
        assert context.playhead_position_beats == 2.5
    
    @patch('time.time')
    def test_slice_range_calculation_playing(self, mock_time):
        """Test slice range calculation when playing"""
        # Setup time progression
        mock_time.return_value = 1000.0
        
        context = MusicalContext()
        context.set_bpm(120.0)  # 2 beats per second
        context.set_playing(True)  # This sets last_update_time
        
        # Change time for next call
        mock_time.return_value = 1000.1  # 100ms elapsed
        
        # Calculate slice range
        start, end = context.get_current_slice_range(512)
        
        # 100ms at 120 BPM = 0.2 beats
        expected_beats = 0.1 * (120.0 / 60.0)  # 0.2 beats
        
        assert start == 0.0
        assert abs(end - expected_beats) < 0.001
        assert abs(context.playhead_position_beats - expected_beats) < 0.001
    
    def test_slice_length_calculation(self):
        """Test slice length in beats calculation"""
        context = MusicalContext()
        context.set_sample_rate(44100.0)
        context.set_bpm(120.0)
        
        # 512 samples at 44100 Hz = ~11.6ms
        # At 120 BPM (2 beats/sec) = ~0.023 beats
        slice_beats = context.get_slice_length_beats(512)
        expected = (512 / 44100.0) * (120.0 / 60.0)
        
        assert abs(slice_beats - expected) < 0.001
    
    def test_beats_samples_conversion(self):
        """Test conversion between beats and samples"""
        context = MusicalContext()
        context.set_sample_rate(44100.0)
        context.set_bpm(120.0)  # 2 beats per second
        
        # 1 beat = 0.5 seconds = 22050 samples
        samples = context.beats_to_samples(1.0)
        assert samples == 22050
        
        # Convert back
        beats = context.samples_to_beats(22050)
        assert abs(beats - 1.0) < 0.001
        
        # Test with different values
        samples = context.beats_to_samples(2.5)
        expected_samples = int(2.5 * 0.5 * 44100.0)
        assert samples == expected_samples
    
    def test_quantized_bar_position(self):
        """Test next quantized bar position calculation"""
        context = MusicalContext()
        context.set_meter(4)
        
        # At beginning
        context.playhead_position_beats = 0.0
        assert context.get_next_quantized_bar_position() == 4.0
        
        # In middle of bar
        context.playhead_position_beats = 2.5
        assert context.get_next_quantized_bar_position() == 4.0
        
        # At bar boundary
        context.playhead_position_beats = 4.0
        assert context.get_next_quantized_bar_position() == 8.0
        
        # With different meter
        context.set_meter(3)
        context.playhead_position_beats = 1.5
        assert context.get_next_quantized_bar_position() == 3.0
    
    def test_playhead_reset(self):
        """Test playhead reset functionality"""
        context = MusicalContext()
        context.playhead_position_beats = 5.5
        context.bar_count = 3
        
        context.reset_playhead()
        
        assert context.playhead_position_beats == 0.0
        assert context.bar_count == 0
    
    def test_serialization(self):
        """Test musical context to_dict conversion"""
        context = MusicalContext()
        context.set_bpm(140.0)
        context.set_meter(3)
        context.set_metronome(True)
        context.set_playing(True)
        context.playhead_position_beats = 2.5
        context.bar_count = 1
        
        data = context.to_dict()
        
        assert data['bpm'] == 140.0
        assert data['meter'] == 3
        assert data['metronome_on'] == True
        assert data['is_playing'] == True
        assert data['playhead_position_beats'] == 2.5
        assert data['bar_count'] == 1
        assert data['doing_count_in'] == False


class TestMusicalContextTiming:
    """Advanced timing tests for MusicalContext"""
    
    @patch('time.time')
    def test_consistent_timing_updates(self, mock_time):
        """Test consistent timing over multiple updates"""
        # Simulate regular 10ms updates
        current_time = 1000.0
        
        def time_side_effect():
            nonlocal current_time
            result = current_time
            current_time += 0.01  # Advance 10ms each call
            return result
        
        mock_time.side_effect = time_side_effect
        
        context = MusicalContext()
        context.set_bpm(120.0)  # 2 beats per second
        context.set_playing(True)
        
        positions = []
        for i in range(5):  # 5 updates
            start, end = context.get_current_slice_range(441)  # ~10ms at 44.1kHz
            positions.append(end)
        
        # Each update should advance by ~0.02 beats (10ms at 120 BPM)
        expected_advance = 0.01 * (120.0 / 60.0)  # 0.02 beats
        
        for i in range(1, len(positions)):
            actual_advance = positions[i] - positions[i-1]
            assert abs(actual_advance - expected_advance) < 0.001
    
    def test_bpm_change_during_playback(self):
        """Test BPM changes affect timing immediately"""
        with patch('time.time') as mock_time:
            current_time = 1000.0
            
            def time_side_effect():
                nonlocal current_time
                result = current_time
                current_time += 0.05  # Advance 50ms each call
                return result
            
            mock_time.side_effect = time_side_effect
            
            context = MusicalContext()
            context.set_bpm(120.0)
            context.set_playing(True)
            
            # First update at 120 BPM
            start1, end1 = context.get_current_slice_range(512)
            
            # Change BPM
            context.set_bpm(240.0)  # Double the BPM
            
            # Second update should use new BPM
            start2, end2 = context.get_current_slice_range(512)
            
            # Second advance should be roughly double the first
            advance1 = end1 - start1
            advance2 = end2 - start2
            
            assert abs(advance2 - (2 * advance1)) < 0.01