import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modes.main_controls_mode import MainControlsMode
import definitions


class TestMainControlsMode(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_app = Mock()
        self.mock_push = Mock()
        self.mock_session = Mock()
        self.mock_state = Mock()
        
        self.mock_app.push = self.mock_push
        self.mock_app.session = self.mock_session
        self.mock_app.state = self.mock_state
        self.mock_app.track_selection_mode = Mock()
        self.mock_app.track_selection_mode.selected_track = 0
        
        # Mock session properties
        self.mock_session.is_playing = False
        self.mock_session.is_recording = False
        self.mock_session.playing = False  # Add this property that's actually used
        self.mock_session.metronome_on = False
        self.mock_session.fixed_length_recording_bars = 0
        self.mock_session.record_automation_enabled = False
        
        # Create mock tracks with clips
        mock_tracks = []
        for i in range(8):
            mock_track = Mock()
            mock_clips = []
            for j in range(4):
                mock_clip = Mock()
                mock_clip.get_status.return_value = 'stopped'  # Default status
                mock_clips.append(mock_clip)
            mock_track.clips = mock_clips
            mock_tracks.append(mock_track)
        self.mock_session.tracks = mock_tracks
        
        self.main_controls = MainControlsMode(self.mock_app)
    
    def test_transport_buttons_state(self):
        """Test transport button state detection"""
        is_playing, is_recording, metronome_on = self.main_controls.get_transport_buttons_state()
        
        self.assertFalse(is_playing)
        self.assertFalse(is_recording)
        self.assertFalse(metronome_on)
    
    def test_play_button_press(self):
        """Test play button functionality"""
        result = self.main_controls.on_button_pressed(self.main_controls.play_button)
        
        self.mock_session.play_stop.assert_called_once()
        self.assertTrue(result)
    
    def test_metronome_button_press(self):
        """Test metronome button functionality"""
        self.mock_app.add_display_notification = Mock()
        
        result = self.main_controls.on_button_pressed(self.main_controls.metronome_button)
        
        self.mock_session.metronome_on_off.assert_called_once()
        self.mock_app.add_display_notification.assert_called_once()
        self.assertTrue(result)
    
    @patch('time.time', return_value=1000.0)
    def test_tap_tempo_functionality(self, mock_time):
        """Test tap tempo calculation"""
        self.mock_app.add_display_notification = Mock()
        
        # Simulate 3 taps at 120 BPM (0.5 second intervals)
        self.main_controls.last_tap_tempo_times = [999.0, 999.5]
        
        result = self.main_controls.on_button_pressed(self.main_controls.tap_tempo_button)
        
        # Should calculate BPM and set it
        self.mock_session.set_bpm.assert_called_once()
        self.mock_app.add_display_notification.assert_called_once()
        self.assertTrue(result)
    
    def test_fixed_length_button_cycle(self):
        """Test fixed length button cycling"""
        self.mock_app.add_display_notification = Mock()
        self.mock_session.meter = 4
        
        # Test normal increment
        result = self.main_controls.on_button_pressed(self.main_controls.fixed_length_button)
        
        self.mock_session.set_fix_length_recording_bars.assert_called_with(1)
        self.mock_app.add_display_notification.assert_called_once()
    
    def test_fixed_length_button_long_press_reset(self):
        """Test fixed length button long press resets to 0"""
        self.mock_app.add_display_notification = Mock()
        
        result = self.main_controls.on_button_pressed(self.main_controls.fixed_length_button, long_press=True)
        
        self.mock_session.set_fix_length_recording_bars.assert_called_with(0)
        self.mock_app.add_display_notification.assert_called_once()
    
    def test_global_record_functionality(self):
        """Test global record functionality"""
        # Setup mock tracks and clips
        mock_track = Mock()
        mock_clip = Mock()
        mock_clip.get_status.return_value = 'p'  # playing
        mock_track.clips = [mock_clip]
        self.mock_session.tracks = [mock_track]
        self.mock_session.get_clip_by_idx.return_value = mock_clip
        
        self.main_controls.global_record()
        
        mock_clip.record_on_off.assert_called_once()
    
    def test_melodic_rhythmic_toggle(self):
        """Test melodic/rhythmic mode toggle"""
        self.mock_app.toggle_melodic_rhythmic_slice_modes = Mock()
        
        result = self.main_controls.on_button_pressed(self.main_controls.melodic_rhythmic_toggle_button)
        
        self.mock_app.toggle_melodic_rhythmic_slice_modes.assert_called_once()
        self.assertTrue(result)
    
    def test_settings_button_toggle(self):
        """Test settings mode toggle"""
        self.mock_app.toggle_and_rotate_settings_mode = Mock()
        
        result = self.main_controls.on_button_pressed(self.main_controls.settings_button)
        
        self.mock_app.toggle_and_rotate_settings_mode.assert_called_once()
        self.assertTrue(result)
    
    def test_record_automation_button(self):
        """Test record automation button"""
        result = self.main_controls.on_button_pressed(self.main_controls.record_automation_button)
        
        self.mock_session.set_record_automation_enabled.assert_called_once()


if __name__ == '__main__':
    unittest.main()