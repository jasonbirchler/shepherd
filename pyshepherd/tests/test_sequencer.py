import pytest
import time
from unittest.mock import Mock, patch
from pyshepherd.backend import Sequencer, Session


class TestSequencer:
    """Test suite for the core Sequencer functionality"""
    
    def test_sequencer_initialization(self):
        """Test sequencer creates with default settings"""
        sequencer = Sequencer(enable_websocket=False)
        
        assert sequencer.sample_rate == 44100.0
        assert sequencer.samples_per_slice == 512
        assert sequencer.is_running == False
        assert sequencer.session is None
        assert sequencer.musical_context is not None
        assert sequencer.hardware_devices is not None
    
    def test_sequencer_prepare(self):
        """Test sequencer preparation with custom settings"""
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare(sample_rate=48000.0, samples_per_slice=256)
        
        assert sequencer.sample_rate == 48000.0
        assert sequencer.samples_per_slice == 256
        assert sequencer.musical_context.sample_rate == 48000.0
    
    def test_new_session_creation(self):
        """Test creating a new session"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=4, num_scenes=2, name="Test Session")
        
        assert sequencer.session == session
        assert session.name == "Test Session"
        assert session.num_tracks == 4
        assert session.num_scenes == 2
        assert len(session.tracks) == 4
        
        # Check each track has correct number of clips
        for track in session.tracks:
            assert len(track.clips) == 2
    
    def test_sequencer_start_stop(self):
        """Test sequencer start/stop functionality"""
        sequencer = Sequencer(enable_websocket=False)
        
        # Start sequencer
        sequencer.start()
        assert sequencer.is_running == True
        assert sequencer._processing_thread is not None
        
        # Stop sequencer
        sequencer.stop()
        assert sequencer.is_running == False
    
    @patch('mido.get_output_names')
    @patch('mido.get_input_names')
    def test_hardware_device_initialization(self, mock_inputs, mock_outputs):
        """Test hardware device initialization"""
        mock_outputs.return_value = ['Test Output 1', 'Test Output 2']
        mock_inputs.return_value = ['Test Input 1']
        
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare()
        
        # Check devices were created
        output_devices = sequencer.hardware_devices.get_output_devices()
        input_devices = sequencer.hardware_devices.get_input_devices()
        
        assert len(output_devices) == 2
        assert len(input_devices) == 1
        assert output_devices[0].midi_device_name == 'Test Output 1'
        assert input_devices[0].midi_device_name == 'Test Input 1'
    
    def test_get_state_dict(self):
        """Test state dictionary generation"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=2, num_scenes=1)
        
        state = sequencer.get_state_dict()
        
        assert 'session' in state
        assert 'musical_context' in state
        assert 'hardware_devices' in state
        assert state['session']['name'] == session.name
        assert state['session']['num_tracks'] == 2
        assert state['session']['num_scenes'] == 1


class TestSequencerIntegration:
    """Integration tests for sequencer with session and tracks"""
    
    def test_session_playback_integration(self):
        """Test session playback affects musical context"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        # Initially not playing
        assert not session.is_playing
        assert not sequencer.musical_context.is_playing
        
        # Start playback
        session.play()
        assert session.is_playing
        assert sequencer.musical_context.is_playing
        
        # Stop playback
        session.stop()
        assert not session.is_playing
        assert not sequencer.musical_context.is_playing
    
    def test_bpm_meter_integration(self):
        """Test BPM and meter changes propagate correctly"""
        sequencer = Sequencer(enable_websocket=False)
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        # Change BPM
        session.set_bpm(140.0)
        assert session.bpm == 140.0
        assert sequencer.musical_context.bpm == 140.0
        
        # Change meter
        session.set_meter(3)
        assert session.meter == 3
        assert sequencer.musical_context.meter == 3
    
    @patch('mido.get_output_names')
    def test_track_device_assignment(self, mock_outputs):
        """Test track hardware device assignment"""
        mock_outputs.return_value = ['Test Synth']
        
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare()
        session = sequencer.new_session(num_tracks=1, num_scenes=1)
        
        track = session.tracks[0]
        track.set_output_device('Out1')  # Should match short name
        
        assert track.output_hardware_device_name == 'Out1'
        device = track.get_output_device()
        assert device is not None
        assert device.short_name == 'Out1'


class TestSequencerPerformance:
    """Performance and timing tests"""
    
    def test_processing_loop_timing(self):
        """Test that processing loop maintains reasonable timing"""
        sequencer = Sequencer(enable_websocket=False)
        sequencer.prepare(sample_rate=44100.0, samples_per_slice=512)
        
        # Calculate expected slice duration
        expected_duration = 512 / 44100.0  # ~11.6ms
        
        # Mock the MIDI processing to be very fast
        original_process = sequencer._process_midi_slice
        call_times = []
        
        def mock_process():
            call_times.append(time.time())
            original_process()
        
        sequencer._process_midi_slice = mock_process
        
        # Run for a short time
        sequencer.start()
        time.sleep(0.1)  # 100ms
        sequencer.stop()
        
        # Check timing consistency
        if len(call_times) > 1:
            intervals = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
            avg_interval = sum(intervals) / len(intervals)
            
            # Should be close to expected duration (within 50% tolerance)
            assert abs(avg_interval - expected_duration) < expected_duration * 0.5