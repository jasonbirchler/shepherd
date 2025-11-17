import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import definitions


class TestDefinitions(unittest.TestCase):
    
    def test_color_constants(self):
        """Test color constant definitions"""
        self.assertEqual(definitions.BLACK, 'black')
        self.assertEqual(definitions.WHITE, 'white')
        self.assertEqual(definitions.RED, 'red')
        self.assertEqual(definitions.GREEN, 'green')
        self.assertEqual(definitions.BLUE, 'blue')
    
    def test_color_rgb_values(self):
        """Test RGB color value retrieval"""
        black_rgb = definitions.get_color_rgb('black')
        self.assertEqual(black_rgb, [0, 0, 0])
        
        white_rgb = definitions.get_color_rgb('white')
        self.assertEqual(white_rgb, [255, 255, 255])
        
        # Test unknown color returns black
        unknown_rgb = definitions.get_color_rgb('unknown_color')
        self.assertEqual(unknown_rgb, [0, 0, 0])
    
    def test_color_rgb_float_values(self):
        """Test RGB float color value retrieval"""
        black_rgb_float = definitions.get_color_rgb_float('black')
        self.assertEqual(black_rgb_float, [0.0, 0.0, 0.0])
        
        white_rgb_float = definitions.get_color_rgb_float('white')
        self.assertEqual(white_rgb_float, [1.0, 1.0, 1.0])
    
    def test_darker_color_generation(self):
        """Test that darker color variants are generated"""
        # Check that darker variants exist
        self.assertIn('black_darker1', definitions.COLORS_NAMES)
        self.assertIn('black_darker2', definitions.COLORS_NAMES)
        self.assertIn('white_darker1', definitions.COLORS_NAMES)
        self.assertIn('white_darker2', definitions.COLORS_NAMES)
    
    def test_timer_class(self):
        """Test Timer class functionality"""
        timer = definitions.Timer()
        self.assertFalse(timer.toClearTimer)
        
        timer.setClearTimer()
        self.assertTrue(timer.toClearTimer)
    
    def test_shepherd_controller_mode_base_class(self):
        """Test ShepherdControllerMode base class"""
        mock_app = object()
        mode = definitions.ShepherdControllerMode(mock_app)
        
        self.assertEqual(mode.app, mock_app)
        self.assertEqual(mode.name, '')
        self.assertIsNone(mode.xor_group)
        self.assertEqual(mode.buttons_used, [])
    
    def test_button_timing_constants(self):
        """Test button timing constants"""
        self.assertEqual(definitions.BUTTON_LONG_PRESS_TIME, 0.5)
        self.assertEqual(definitions.BUTTON_DOUBLE_PRESS_TIME, 0.2)
    
    def test_notification_time_constant(self):
        """Test notification time constant"""
        self.assertEqual(definitions.NOTIFICATION_TIME, 3)
    
    def test_layout_constants(self):
        """Test layout constants"""
        self.assertEqual(definitions.LAYOUT_MELODIC, 'lmelodic')
        self.assertEqual(definitions.LAYOUT_RHYTHMIC, 'lrhythmic')
        self.assertEqual(definitions.LAYOUT_SLICES, 'lslices')
    
    def test_file_paths_creation(self):
        """Test that file paths are properly created"""
        self.assertTrue(definitions.BASE_DATA_DIR.endswith('Shepherd'))
        self.assertTrue(definitions.SETTINGS_FILE_PATH.endswith('controllerSettings.json'))
        self.assertTrue(definitions.DEVICE_DEFINITION_FOLDER.endswith('device_definitions'))


if __name__ == '__main__':
    unittest.main()