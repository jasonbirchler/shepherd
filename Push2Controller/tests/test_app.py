import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import definitions


class TestShepherdPush2ControllerApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with mocked dependencies"""
        self.mock_push = Mock()
        self.mock_session = Mock()
        self.mock_state = Mock()
        
        # Mock pyshepherd
        self.mock_shepherd_interface = Mock()
        self.mock_shepherd_interface.state = self.mock_state
        
        # Patch external dependencies
        self.patches = [
            patch('push2_python.Push2', return_value=self.mock_push),
            patch('mido.get_output_names', return_value=['Test MIDI Out']),
            patch('mido.get_input_names', return_value=['Test MIDI In']),
            patch('subprocess.Popen'),
            patch('time.sleep'),
        ]
        
        for p in self.patches:
            p.start()
    
    def tearDown(self):
        """Clean up patches"""
        for p in self.patches:
            p.stop()
    
    @patch('app.ShepherdPush2ControllerApp.__init__', return_value=None)
    def test_mode_activation(self, mock_init):
        """Test mode activation and deactivation"""
        test_app = app.ShepherdPush2ControllerApp()
        test_app.active_modes = []
        test_app.previously_active_mode_for_xor_group = {}
        
        # Create mock mode
        mock_mode = Mock()
        mock_mode.xor_group = 'test_group'
        mock_mode.activate = Mock()
        mock_mode.deactivate = Mock()
        
        # Test mode activation
        test_app.set_mode_for_xor_group(mock_mode)
        self.assertIn(mock_mode, test_app.active_modes)
        mock_mode.activate.assert_called_once()
    
    @patch('app.ShepherdPush2ControllerApp.__init__', return_value=None)
    def test_settings_mode_toggle(self, mock_init):
        """Test settings mode toggle functionality"""
        test_app = app.ShepherdPush2ControllerApp()
        test_app.active_modes = []
        test_app.settings_mode = Mock()
        test_app.settings_mode.move_to_next_page = Mock(return_value=False)
        test_app.settings_mode.activate = Mock()
        test_app.settings_mode.deactivate = Mock()
        
        # Test activation
        test_app.toggle_and_rotate_settings_mode()
        self.assertIn(test_app.settings_mode, test_app.active_modes)
        test_app.settings_mode.activate.assert_called_once()
        
        # Test page rotation
        test_app.toggle_and_rotate_settings_mode()
        test_app.settings_mode.move_to_next_page.assert_called_once()
    
    @patch('app.ShepherdPush2ControllerApp.__init__', return_value=None)
    def test_melodic_rhythmic_toggle(self, mock_init):
        """Test melodic/rhythmic mode toggle"""
        test_app = app.ShepherdPush2ControllerApp()
        test_app.active_modes = []
        test_app.melodic_mode = Mock()
        test_app.rhyhtmic_mode = Mock()
        test_app.slice_notes_mode = Mock()
        test_app.set_mode_for_xor_group = Mock()
        
        # Test melodic -> rhythmic
        test_app.is_mode_active = Mock(side_effect=lambda mode: mode == test_app.melodic_mode)
        test_app.toggle_melodic_rhythmic_slice_modes()
        test_app.set_mode_for_xor_group.assert_called_with(test_app.rhyhtmic_mode)
        
        # Test rhythmic -> slice
        test_app.is_mode_active = Mock(side_effect=lambda mode: mode == test_app.rhyhtmic_mode)
        test_app.toggle_melodic_rhythmic_slice_modes()
        test_app.set_mode_for_xor_group.assert_called_with(test_app.slice_notes_mode)


if __name__ == '__main__':
    unittest.main()