import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_mido():
    """Mock mido MIDI library for all tests"""
    with patch('mido.get_output_names') as mock_outputs, \
         patch('mido.get_input_names') as mock_inputs, \
         patch('mido.open_output') as mock_open_output, \
         patch('mido.open_input') as mock_open_input:
        
        # Default return values
        mock_outputs.return_value = ['Test Output']
        mock_inputs.return_value = ['Test Input']
        
        # Mock MIDI ports
        mock_output_port = Mock()
        mock_input_port = Mock()
        mock_input_port.iter_pending.return_value = []
        
        mock_open_output.return_value = mock_output_port
        mock_open_input.return_value = mock_input_port
        
        yield {
            'outputs': mock_outputs,
            'inputs': mock_inputs,
            'open_output': mock_open_output,
            'open_input': mock_open_input,
            'output_port': mock_output_port,
            'input_port': mock_input_port
        }


@pytest.fixture
def mock_sequencer():
    """Mock sequencer for testing components in isolation"""
    sequencer = Mock()
    sequencer.musical_context = Mock()
    sequencer.hardware_devices = Mock()
    sequencer.sample_rate = 44100.0
    sequencer.samples_per_slice = 512
    return sequencer


@pytest.fixture
def mock_session():
    """Mock session for testing tracks and clips"""
    session = Mock()
    session.sequencer = Mock()
    session.sequencer.musical_context = Mock()
    session.sequencer.hardware_devices = Mock()
    return session


@pytest.fixture
def mock_track():
    """Mock track for testing clips"""
    track = Mock()
    track.session = Mock()
    track.send_midi_message = Mock()
    return track


@pytest.fixture(autouse=True)
def disable_websocket():
    """Disable WebSocket server for all tests by default"""
    with patch('pyshepherd.server.websocket_server.WebSocketServer'):
        yield