import pytest
from unittest.mock import Mock
from pyshepherd.backend import Track, Clip


class TestTrack:
    """Test suite for Track functionality"""
    
    def test_track_creation(self):
        """Test track creation with clips"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=3, session=session)
        
        assert track.name == "Test Track"
        assert track.session == session
        assert len(track.clips) == 3
        assert track.output_hardware_device_name == ""
        assert track.input_monitoring == False
        
        # Check clip names
        for i, clip in enumerate(track.clips):
            assert clip.name == f"Test Track Clip {i+1}"
    
    def test_track_device_assignment(self):
        """Test hardware device assignment"""
        session = Mock()
        session.sequencer = Mock()
        session.sequencer.hardware_devices = Mock()
        
        mock_device = Mock()
        session.sequencer.hardware_devices.get_output_device.return_value = mock_device
        
        track = Track("Test Track", num_scenes=1, session=session)
        
        # Set output device
        track.set_output_device("Synth1")
        assert track.output_hardware_device_name == "Synth1"
        
        # Get output device
        device = track.get_output_device()
        assert device == mock_device
        session.sequencer.hardware_devices.get_output_device.assert_called_with("Synth1")
    
    def test_track_midi_message_sending(self):
        """Test MIDI message routing through track"""
        session = Mock()
        session.sequencer = Mock()
        session.sequencer.hardware_devices = Mock()
        
        mock_device = Mock()
        session.sequencer.hardware_devices.get_output_device.return_value = mock_device
        
        track = Track("Test Track", num_scenes=1, session=session)
        track.set_output_device("Synth1")
        
        # Send MIDI message
        mock_message = Mock()
        track.send_midi_message(mock_message)
        
        mock_device.send_message.assert_called_once_with(mock_message)
    
    def test_track_clip_management(self):
        """Test clip retrieval and playback"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=3, session=session)
        
        # Mock clip methods
        for clip in track.clips:
            clip.play = Mock()
            clip.stop = Mock()
            clip.is_playing = False
        
        # Get clip by index
        clip = track.get_clip(1)
        assert clip == track.clips[1]
        
        # Invalid index
        assert track.get_clip(5) is None
        
        # Play specific clip
        track.play_clip(1)
        track.clips[1].play.assert_called_once()
        
        # Stop all clips
        track.stop_all_clips()
        for clip in track.clips:
            clip.stop.assert_called_once()
    
    def test_track_clip_exclusivity(self):
        """Test that only one clip plays at a time per track"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=3, session=session)
        
        # Mock clip methods and states
        for i, clip in enumerate(track.clips):
            clip.play = Mock()
            clip.stop = Mock()
            clip.is_playing = (i == 0)  # First clip is playing
        
        # Play second clip - should stop first clip
        track.play_clip(1)
        
        track.clips[0].stop.assert_called_once()  # Stop currently playing
        track.clips[1].play.assert_called_once()  # Play new clip
        track.clips[2].stop.assert_not_called()   # Don't affect others
    
    def test_track_process_slice(self):
        """Test track slice processing"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=2, session=session)
        
        # Mock clip processing
        for clip in track.clips:
            clip.is_playing = True
            clip.process_slice = Mock()
        
        # Process slice
        slice_range = (0.0, 0.5)
        track.process_slice(slice_range)
        
        # All playing clips should be processed
        for clip in track.clips:
            clip.process_slice.assert_called_once_with(slice_range)
    
    def test_track_input_monitoring(self):
        """Test input monitoring functionality"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=1, session=session)
        
        # Enable monitoring
        track.set_input_monitoring(True)
        assert track.input_monitoring == True
        
        # Disable monitoring
        track.set_input_monitoring(False)
        assert track.input_monitoring == False
    
    def test_track_serialization(self):
        """Test track to_dict conversion"""
        session = Mock()
        
        track = Track("Test Track", num_scenes=2, session=session)
        track.set_output_device("Synth1")
        track.set_input_monitoring(True)
        
        data = track.to_dict()
        
        assert data['name'] == "Test Track"
        assert data['output_hardware_device_name'] == "Synth1"
        assert data['input_monitoring'] == True
        assert len(data['clips']) == 2
        assert 'uuid' in data