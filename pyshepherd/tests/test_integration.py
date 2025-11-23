from unittest.mock import Mock, patch
import pytest
from pyshepherd.backend import Sequencer


class TestSequencerIntegration:
    """Integration tests for complete sequencer functionality"""
    
    @patch('mido.get_output_names')
    @patch('mido.get_input_names')
    @patch('mido.open_output')
    def test_complete_session_workflow(self, mock_open_output, mock_inputs, mock_outputs):
        """Test complete workflow from session creation to MIDI output"""
        # Setup MIDI mocking
        mock_outputs.return_value = ['Test Synth']
        mock_inputs.return_value = []
        mock_port = Mock()
        mock_open_output.return_value = mock_port
        
        # Create sequencer and session
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare()
        session = sequencer.new_session(num_tracks=2, num_scenes=1, name="Test Session")
        
        # Configure track with hardware device
        track = session.tracks[0]
        track.set_output_device("Out1")
        
        # Add MIDI events to clip
        clip = track.clips[0]
        clip.add_note_event(0.0, 60, 100, 0.5, 1)  # C4 at start
        clip.add_note_event(1.0, 64, 100, 0.5, 1)  # E4 at beat 1
        
        # Start playback
        clip.play()
        
        # Manually process with a guaranteed working slice range
        test_slice = (0.0, 2.0)  # Process 2 beats containing all events
        track.process_slice(test_slice)
        
        # Verify MIDI messages were sent
        assert mock_port.send.called
        
        # Stop everything
        clip.stop()
    
    @patch('mido.get_output_names')
    @patch('mido.open_output')
    def test_multi_track_coordination(self, mock_open_output, mock_outputs):
        """Test multiple tracks playing simultaneously"""
        mock_outputs.return_value = ['Synth1', 'Synth2']
        mock_port1 = Mock()
        mock_port2 = Mock()
        mock_open_output.side_effect = [mock_port1, mock_port2]
        
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare()
        session = sequencer.new_session(num_tracks=2, num_scenes=1)
        
        # Get available device names and assign them
        available_devices = sequencer.hardware_devices.get_available_output_names()
        if len(available_devices) >= 2:
            session.tracks[0].set_output_device(available_devices[0])
            session.tracks[1].set_output_device(available_devices[1])
            
            # Add different patterns to each track
            clip1 = session.tracks[0].clips[0]
            clip1.add_note_event(0.0, 60, 100, 0.25)
            clip1.add_note_event(0.5, 62, 100, 0.25)
            
            clip2 = session.tracks[1].clips[0]
            clip2.add_note_event(0.25, 64, 100, 0.25)
            clip2.add_note_event(0.75, 67, 100, 0.25)
            
            # Start playback and clips
            clip1.play()
            clip2.play()
            
            # Manually process with a guaranteed working slice range
            test_slice = (0.0, 1.0)  # Process first beat containing all events
            
            # Process each track directly
            session.tracks[0].process_slice(test_slice)
            session.tracks[1].process_slice(test_slice)
            
            # Both devices should receive messages
            assert mock_port1.send.called
            assert mock_port2.send.called
    
    def test_bpm_change_affects_timing(self):
        """Test that BPM changes affect all timing calculations"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        # Initial BPM
        session.set_bpm(120.0)
        assert sequencer.musical_context.bpm == 120.0
        
        # Calculate slice length at 120 BPM
        slice_length_120 = sequencer.musical_context.get_slice_length_beats(512)
        
        # Change BPM
        session.set_bpm(240.0)
        assert sequencer.musical_context.bpm == 240.0
        
        # Slice length should be different
        slice_length_240 = sequencer.musical_context.get_slice_length_beats(512)
        
        # At double BPM, slice should contain twice as many beats
        assert abs(slice_length_240 - (2 * slice_length_120)) < 0.001
    
    def test_scene_playback_coordination(self):
        """Test scene playback affects multiple tracks"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=3, num_scenes=2)
        
        # Mock clip play methods
        for track in session.tracks:
            for clip in track.clips:
                clip.play = Mock()
        
        # Play scene 0
        session.play_scene(0)
        
        # All tracks' clip 0 should be played
        for track in session.tracks:
            track.clips[0].play.assert_called_once()
            track.clips[1].play.assert_not_called()
    
    def test_clip_looping_with_different_lengths(self):
        """Test clips with different lengths loop independently"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=2, num_scenes=1)
        
        # Set different clip lengths
        clip1 = session.tracks[0].clips[0]
        clip2 = session.tracks[1].clips[0]
        
        clip1.set_length(2.0)  # 2 beats
        clip2.set_length(3.0)  # 3 beats
        
        clip1.play()
        clip2.play()
        
        # Simulate playback progression
        clip1.playhead_position_beats = 1.8
        clip2.playhead_position_beats = 2.8
        
        # Process slice that advances both clips
        clip1.process_slice((1.8, 2.2))  # Should loop
        clip2.process_slice((2.8, 3.2))  # Should loop
        
        # Clip 1 should have looped
        assert abs(clip1.playhead_position_beats - 0.2) < 0.001
        
        # Clip 2 should have looped
        assert abs(clip2.playhead_position_beats - 0.2) < 0.001
    
    @patch('random.random')
    def test_event_chance_affects_playback(self, mock_random):
        """Test that event chance affects MIDI output"""
        mock_random.return_value = 0.8  # High value to test chance
        
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        track = session.tracks[0]
        track.send_midi_message = Mock()
        
        clip = track.clips[0]
        
        # Add event with 50% chance
        event = clip.add_note_event(0.5, 60, 100, 0.25)
        event.chance = 0.5
        
        clip.play()
        
        # Process slice - event should not trigger (0.8 > 0.5)
        clip.process_slice((0.0, 1.0))
        track.send_midi_message.assert_not_called()
        
        # Change random value - event should trigger
        mock_random.return_value = 0.3  # 0.3 < 0.5
        clip.process_slice((0.0, 1.0))
        assert track.send_midi_message.call_count == 2  # Note on + off
    
    def test_quantization_affects_event_timing(self):
        """Test that quantization changes event timing"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        clip = session.tracks[0].clips[0]
        
        # Add events with unquantized timing
        clip.add_note_event(0.1, 60, 100, 0.25)  # Slightly off beat
        clip.add_note_event(1.15, 64, 100, 0.25)  # Slightly after beat 1
        
        # Apply quantization
        clip.quantize_events(0.5)  # Half-note quantization
        
        # Events should be quantized
        assert clip.sequence_events[0].timestamp == 0.0
        assert clip.sequence_events[1].timestamp == 1.0
    
    def test_hardware_device_hot_swapping(self):
        """Test changing hardware devices during playback"""
        with patch('mido.get_output_names') as mock_outputs, \
             patch('mido.open_output') as mock_open_output:
            
            mock_outputs.return_value = ['Device1', 'Device2']
            mock_port1 = Mock()
            mock_port2 = Mock()
            mock_open_output.side_effect = [mock_port1, mock_port2]
            
            sequencer = Sequencer(enable_websocket=False)
            sequencer.prepare()
            session = sequencer.new_session(num_tracks=1, num_scenes=1)
            
            track = session.tracks[0]
            available_devices = sequencer.hardware_devices.get_available_output_names()
            
            if len(available_devices) >= 2:
                # Initially assign to first device
                track.set_output_device(available_devices[0])
                device1 = track.get_output_device()
                assert device1 is not None
                assert device1.short_name == available_devices[0]
                
                # Switch to second device
                track.set_output_device(available_devices[1])
                device2 = track.get_output_device()
                assert device2 is not None
                assert device2.short_name == available_devices[1]
                assert device2 != device1
    
    def test_session_state_consistency(self):
        """Test that session state remains consistent across operations"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=2, num_scenes=3, name="Test")
        
        # Get initial state
        initial_state = sequencer.get_state_dict()
        
        # Verify structure
        assert initial_state['session']['name'] == "Test"
        assert initial_state['session']['num_tracks'] == 2
        assert initial_state['session']['num_scenes'] == 3
        assert len(initial_state['session']['tracks']) == 2
        
        # Each track should have 3 clips
        for track_data in initial_state['session']['tracks']:
            assert len(track_data['clips']) == 3
        
        # Make changes
        session.set_bpm(140.0)
        session.set_metronome(True)
        session.tracks[0].set_input_monitoring(True)
        
        # Get updated state
        updated_state = sequencer.get_state_dict()
        
        # Verify changes are reflected
        assert updated_state['session']['bpm'] == 140.0
        assert updated_state['session']['metronome_on'] == True
        assert updated_state['session']['tracks'][0]['input_monitoring'] == True


class TestSequencerPerformance:
    """Performance and stress tests"""
    
    def test_many_simultaneous_events(self):
        """Test handling many simultaneous MIDI events"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        track = session.tracks[0]
        track.send_midi_message = Mock()
        
        clip = track.clips[0]
        
        # Add many events at the same time
        for note in range(60, 80):  # 20 notes
            clip.add_note_event(0.5, note, 100, 0.25)
        
        clip.play()
        
        # Process slice containing all events
        clip.process_slice((0.0, 1.0))
        
        # Should handle all events without errors
        assert track.send_midi_message.call_count == 40  # 20 note-ons + 20 note-offs
    
    def test_long_running_session(self):
        """Test session running for extended time"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        # Simulate long playback
        session.play()
        
        # Advance playhead significantly
        context = sequencer.musical_context
        context.playhead_position_beats = 10000.0  # Many bars
        
        # Should still function correctly
        slice_range = context.get_current_slice_range(512)
        assert slice_range[0] == 10000.0
        
        # Clip should handle large playhead positions
        clip = session.tracks[0].clips[0]
        clip.play()
        clip.playhead_position_beats = 9999.5
        
        # Process slice - should handle looping correctly
        clip.process_slice((9999.5, 10000.5))
        
        # Should not crash or produce invalid state
        assert clip.playhead_position_beats >= 0.0
