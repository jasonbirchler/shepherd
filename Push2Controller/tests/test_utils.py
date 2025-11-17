import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils


class TestUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_ctx = Mock()
    
    def test_show_title(self):
        """Test show_title function"""
        utils.show_title(self.mock_ctx, 100, 200, 'TEST TITLE')
        
        # Verify text drawing was called
        self.mock_ctx.show_text.assert_called_with('TEST TITLE')
        self.mock_ctx.move_to.assert_called()
    
    def test_show_value(self):
        """Test show_value function with default color"""
        utils.show_value(self.mock_ctx, 100, 200, 'TEST VALUE')
        
        # Verify text drawing was called
        self.mock_ctx.show_text.assert_called_with('TEST VALUE')
        self.mock_ctx.move_to.assert_called()
    
    def test_show_value_with_custom_color(self):
        """Test show_value function with custom color"""
        custom_color = [0.5, 0.5, 0.5]
        utils.show_value(self.mock_ctx, 100, 200, 'TEST VALUE', custom_color)
        
        # Verify color was set
        self.mock_ctx.set_source_rgb.assert_called_with(0.5, 0.5, 0.5)
        self.mock_ctx.show_text.assert_called_with('TEST VALUE')
    
    def test_draw_text_at(self):
        """Test draw_text_at function"""
        utils.draw_text_at(self.mock_ctx, 50, 75, 'TEST TEXT')
        
        # Verify positioning and text drawing
        self.mock_ctx.move_to.assert_called_with(50, 75)
        self.mock_ctx.show_text.assert_called_with('TEST TEXT')
    
    def test_show_notification(self):
        """Test show_notification function"""
        utils.show_notification(self.mock_ctx, 'Test notification')
        
        # Verify notification drawing operations
        self.mock_ctx.rectangle.assert_called()
        self.mock_ctx.fill.assert_called()
        self.mock_ctx.show_text.assert_called_with('Test notification')
    
    def test_show_notification_with_opacity(self):
        """Test show_notification function with custom opacity"""
        utils.show_notification(self.mock_ctx, 'Test notification', opacity=0.5)
        
        # Verify opacity was applied
        self.mock_ctx.set_source_rgba.assert_called()
        self.mock_ctx.show_text.assert_called_with('Test notification')
    
    @patch('utils.push2_python.constants.DISPLAY_LINE_PIXELS', 960)
    @patch('utils.push2_python.constants.DISPLAY_N_LINES', 160)
    def test_notification_positioning(self):
        """Test notification positioning calculations"""
        utils.show_notification(self.mock_ctx, 'Test')
        
        # Verify rectangle positioning uses display constants
        self.mock_ctx.rectangle.assert_called()
        # The exact positioning depends on text measurement, just verify it was called
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        utils.show_title(self.mock_ctx, 100, 200, '')
        utils.show_value(self.mock_ctx, 100, 200, '')
        utils.draw_text_at(self.mock_ctx, 50, 75, '')
        
        # Should still call show_text even with empty string
        self.assertEqual(self.mock_ctx.show_text.call_count, 3)
    
    def test_font_size_setting(self):
        """Test that font size is set in utility functions"""
        utils.show_title(self.mock_ctx, 100, 200, 'TEST')
        
        # Verify font size was set
        self.mock_ctx.set_font_size.assert_called()


if __name__ == '__main__':
    unittest.main()