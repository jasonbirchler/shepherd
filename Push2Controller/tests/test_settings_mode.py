import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modes.settings_mode import SettingsMode, Pages
import definitions


class TestSettingsMode(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_app = Mock()
        self.mock_push = Mock()
        self.mock_push.encoders.available_names = ['encoder_1', 'encoder_2']
        self.mock_app.push = self.mock_push
        self.mock_session = Mock()
        self.mock_app.session = self.mock_session
        
        self.settings_mode = SettingsMode(self.mock_app)
    
    def test_pages_enum(self):
        """Test Pages enum values"""
        self.assertEqual(Pages.PERFORMANCE, 0)
        self.assertEqual(Pages.VARIOUS, 1)
        self.assertEqual(Pages.DEVICES, 2)
        self.assertEqual(Pages.ABOUT, 3)
        self.assertEqual(len(Pages), 4)
    
    def test_page_navigation(self):
        """Test page navigation functionality"""
        self.settings_mode.current_page = 0
        
        # Test normal page advance
        result = self.settings_mode.move_to_next_page()
        self.assertEqual(self.settings_mode.current_page, 1)
        self.assertFalse(result)
        
        # Test wrap around
        self.settings_mode.current_page = 3
        result = self.settings_mode.move_to_next_page()
        self.assertEqual(self.settings_mode.current_page, 0)
        self.assertTrue(result)
    
    def test_track_selection_initialization(self):
        """Test track selection states initialization"""
        self.settings_mode.initialize()
        
        # Check all 8 tracks initialized to device selection (0)
        for i in range(8):
            self.assertEqual(self.settings_mode.track_selection_states[i], 0)
    
    def test_encoder_accumulator_initialization(self):
        """Test encoder accumulator initialization"""
        self.mock_push.encoders.available_names = ['encoder_1', 'encoder_2']
        self.settings_mode.initialize()
        
        for encoder_name in self.mock_push.encoders.available_names:
            self.assertEqual(self.settings_mode.encoder_accumulators[encoder_name], 0)
    
    @patch('modes.settings_mode.time.time', return_value=1000.0)
    def test_encoder_state_initialization(self, mock_time):
        """Test encoder state initialization with timestamps"""
        self.mock_push.encoders.available_names = ['encoder_1', 'encoder_2']
        self.settings_mode.initialize()
        
        for encoder_name in self.mock_push.encoders.available_names:
            self.assertEqual(
                self.settings_mode.encoders_state[encoder_name]['last_message_received'], 
                1000.0
            )
    
    def test_button_color_updates_performance_page(self):
        """Test button color updates for performance page"""
        self.settings_mode.current_page = Pages.PERFORMANCE
        self.settings_mode.update_buttons()
        
        # Check first two buttons are white (active)
        import push2_python.constants
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_UPPER_ROW_1, 
            definitions.WHITE
        )
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_UPPER_ROW_2, 
            definitions.WHITE
        )
    
    def test_button_color_updates_devices_page(self):
        """Test button color updates for devices page"""
        self.settings_mode.current_page = Pages.DEVICES
        self.settings_mode.update_buttons()
        
        # Check all 8 buttons are white and up/down buttons are enabled
        import push2_python.constants
        for i in range(1, 9):
            button_name = getattr(push2_python.constants, f'BUTTON_UPPER_ROW_{i}')
            self.mock_push.buttons.set_button_color.assert_any_call(button_name, definitions.WHITE)
        
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_UP, 
            definitions.WHITE
        )
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_DOWN, 
            definitions.WHITE
        )
    
    def test_deactivate_clears_buttons(self):
        """Test deactivate method clears all buttons"""
        self.settings_mode.deactivate()
        
        # Check all buttons set to black
        import push2_python.constants
        for i in range(1, 9):
            button_name = getattr(push2_python.constants, f'BUTTON_UPPER_ROW_{i}')
            self.mock_push.buttons.set_button_color.assert_any_call(button_name, definitions.BLACK)
        
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_UP, 
            definitions.BLACK
        )
        self.mock_push.buttons.set_button_color.assert_any_call(
            push2_python.constants.BUTTON_DOWN, 
            definitions.BLACK
        )


if __name__ == '__main__':
    unittest.main()