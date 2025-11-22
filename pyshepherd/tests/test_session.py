import pytest
from unittest.mock import Mock
from pyshepherd.backend import Sequencer, Session, Track


class TestSession:
    """Test suite for Session functionality"""
    
    def test_session_creation(self):
        """Test session creation with tracks and clips"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        
        session = Session("Test Session", num_tracks=3, num_scenes=2, sequencer=sequencer)
        
        assert session.name == "Test Session"
        assert session.num_tracks == 3
        assert session.num_scenes == 2
        assert len(session.tracks) == 3
        
        # Each track should have 2 clips
        for track in session.tracks:
            assert len(track.clips) == 2
    
    def test_session_playback_control(self):
        """Test session play/stop functionality"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        
        session = Session("Test", num_tracks=1, num_scenes=1, sequencer=sequencer)
        
        # Test play
        session.play()
        sequencer.musical_context.set_playing.assert_called_with(True)
        
        # Test stop
        session.stop()
        sequencer.musical_context.set_playing.assert_called_with(False)
        
        # Test toggle
        sequencer.musical_context.is_playing = False
        session.play_stop_toggle()
        sequencer.musical_context.set_playing.assert_called_with(True)
    
    def test_session_musical_settings(self):
        """Test BPM, meter, and metronome settings"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        
        session = Session("Test", num_tracks=1, num_scenes=1, sequencer=sequencer)
        
        # Test BPM
        session.set_bpm(140.0)
        sequencer.musical_context.set_bpm.assert_called_with(140.0)
        
        # Test meter
        session.set_meter(3)
        sequencer.musical_context.set_meter.assert_called_with(3)
        
        # Test metronome
        session.set_metronome(True)
        sequencer.musical_context.set_metronome.assert_called_with(True)
    
    def test_scene_playback(self):
        """Test scene playback functionality"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        
        session = Session("Test", num_tracks=2, num_scenes=3, sequencer=sequencer)
        
        # Mock clip play methods
        for track in session.tracks:
            for clip in track.clips:
                clip.play = Mock()
        
        # Play scene 1
        session.play_scene(1)
        
        # Check that clip 1 in each track was played
        for track in session.tracks:
            track.clips[1].play.assert_called_once()
            track.clips[0].play.assert_not_called()
            track.clips[2].play.assert_not_called()
    
    def test_get_track(self):
        """Test track retrieval by index"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        
        session = Session("Test", num_tracks=3, num_scenes=1, sequencer=sequencer)
        
        # Valid indices
        assert session.get_track(0) == session.tracks[0]
        assert session.get_track(2) == session.tracks[2]
        
        # Invalid indices
        assert session.get_track(-1) is None
        assert session.get_track(3) is None
    
    def test_session_properties(self):
        """Test session property access"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        sequencer.musical_context.is_playing = True
        sequencer.musical_context.bpm = 120.0
        sequencer.musical_context.meter = 4
        sequencer.musical_context.metronome_on = False
        
        session = Session("Test", num_tracks=1, num_scenes=1, sequencer=sequencer)
        
        assert session.is_playing == True
        assert session.bpm == 120.0
        assert session.meter == 4
        assert session.metronome_on == False
    
    def test_session_serialization(self):
        """Test session to_dict conversion"""
        sequencer = Mock()
        sequencer.musical_context = Mock()
        sequencer.musical_context.is_playing = False
        sequencer.musical_context.bpm = 120.0
        sequencer.musical_context.meter = 4
        sequencer.musical_context.metronome_on = True
        
        session = Session("Test Session", num_tracks=2, num_scenes=1, sequencer=sequencer)
        
        data = session.to_dict()
        
        assert data['name'] == "Test Session"
        assert data['num_tracks'] == 2
        assert data['num_scenes'] == 1
        assert data['is_playing'] == False
        assert data['bpm'] == 120.0
        assert data['meter'] == 4
        assert data['metronome_on'] == True
        assert len(data['tracks']) == 2