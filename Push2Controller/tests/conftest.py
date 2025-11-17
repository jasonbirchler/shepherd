import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_push2():
    """Mock Push2 device"""
    mock = Mock()
    mock.buttons = Mock()
    mock.pads = Mock()
    mock.encoders = Mock()
    mock.display = Mock()
    mock.encoders.available_names = ['encoder_1', 'encoder_2', 'encoder_3', 'encoder_4', 
                                     'encoder_5', 'encoder_6', 'encoder_7', 'encoder_8']
    return mock


@pytest.fixture
def mock_session():
    """Mock Shepherd session"""
    mock = Mock()
    mock.is_playing = False
    mock.is_recording = False
    mock.metronome_on = False
    mock.fixed_length_recording_bars = 0
    mock.record_automation_enabled = False
    mock.meter = 4
    mock.tracks = [Mock() for _ in range(8)]
    return mock


@pytest.fixture
def mock_app(mock_push2, mock_session):
    """Mock Shepherd app"""
    mock = Mock()
    mock.push = mock_push2
    mock.session = mock_session
    mock.state = Mock()
    mock.active_modes = []
    mock.buttons_need_update = False
    mock.pads_need_update = False
    return mock


@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Auto-mock external dependencies for all tests"""
    with patch('mido.get_output_names', return_value=['Test MIDI Out']), \
         patch('mido.get_input_names', return_value=['Test MIDI In']), \
         patch('subprocess.Popen'), \
         patch('time.sleep'):
        yield