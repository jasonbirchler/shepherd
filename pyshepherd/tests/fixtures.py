"""
Test fixtures for mocking backend components.
These Mock* classes are used exclusively for testing and should not be used in application code.
"""


class MockHardwareDevice:
    """Mock hardware device for testing"""
    
    def __init__(self, device_data):
        self._data = device_data
        self._midi_cc_values = {}  # Store current MIDI CC values
        self._control_change_mapping = {}  # Maps encoder numbers to CC numbers
    
    def __getattr__(self, name):
        return self._data.get(name)
    
    def set_control_change_mapping(self, mapping):
        """Set control change mapping for encoders - mock implementation"""
        self._control_change_mapping = {}
        for encoder_num, cc_number in enumerate(mapping):
            if cc_number >= 0:  # Only map enabled encoders
                self._control_change_mapping[encoder_num] = cc_number
    
    def get_current_midi_cc_parameter_value(self, cc_number):
        """Get current MIDI CC parameter value"""
        return self._midi_cc_values.get(cc_number, 0)
    
    def set_midi_cc_parameter_value(self, cc_number, value):
        """Set MIDI CC parameter value"""
        # Clamp value to 0-127 range
        value = max(0, min(127, value))
        self._midi_cc_values[cc_number] = value
    
    def handle_control_change(self, cc_number, value):
        """Handle incoming control change message - mock implementation"""
        self._midi_cc_values[cc_number] = value


class MockState:
    """Mock state object for testing"""
    
    def __init__(self, state_data):
        self._data = state_data
        self.notes_monitoring_device_name = ""
    
    def __getattr__(self, name):
        return self._data.get(name)
    
    def get_input_hardware_device_by_name(self, name):
        """Get input hardware device by name - mock implementation"""
        devices = self._data.get('hardware_devices', {}).get('devices', [])
        for device in devices:
            if device.get('type') == 'input' and device.get('midi_device_name') == name:
                return MockHardwareDevice(device)
        return None
    
    def get_output_hardware_device_by_name(self, name):
        """Get output hardware device by name - mock implementation"""
        # First try to find in hardware_devices list
        devices = self._data.get('hardware_devices', {}).get('devices', [])
        for device in devices:
            if device.get('type') == 'output' and device.get('midi_device_name') == name:
                return MockHardwareDevice(device)
        
        # If not found and name is provided, create a default mock device
        # This allows the system to work even without explicit hardware device definitions
        if name:
            return MockHardwareDevice({'type': 'output', 'name': name})
        
        return None
    
    def get_available_output_hardware_device_names(self):
        """Get list of available output device names - mock implementation"""
        return self._data.get('hardware_devices', {}).get('available_outputs', [])
    
    def toggle_shepherd_backend_debug_synth(self):
        """Toggle debug synth - mock implementation (no-op)"""
        pass


class MockClip:
    """Mock clip object for testing"""
    
    def __init__(self, clip_data, track):
        self._data = clip_data
        self._track = track
    
    @property
    def name(self):
        return self._data.get('name', '')
    
    @property
    def playing(self):
        return self._data.get('is_playing', False)
    
    @property
    def recording(self):
        return self._data.get('is_recording', False)
    
    @property
    def clip_length_in_beats(self):
        return self._data.get('length_beats', 4.0)
    
    def get_status(self):
        """Get clip status as a string with status characters
        
        Status characters:
        - 'p': playing
        - 'r': recording
        - 'w': will record (cued to record)
        - 'W': will record (fixed length)
        - 'C': cued to play
        """
        status = ''
        if self._data.get('is_playing', False):
            status += 'p'
        if self._data.get('is_recording', False):
            status += 'r'
        if self._data.get('will_record', False):
            status += 'w'
        if self._data.get('will_record_fixed_length', False):
            status += 'W'
        if self._data.get('cued_to_play', False):
            status += 'C'
        return status
    
    def record_on_off(self):
        """Toggle recording state - mock implementation"""
        self._data['is_recording'] = not self._data.get('is_recording', False)


class MockTrack:
    """Mock track object for testing"""
    
    def __init__(self, track_data, session):
        self._data = track_data
        self._session = session
        
        # Create mock clips
        self.clips = []
        for clip_data in track_data.get('clips', []):
            self.clips.append(MockClip(clip_data, self))
    
    @property
    def name(self):
        return self._data.get('name', '')
    
    @property
    def input_monitoring(self):
        return self._data.get('input_monitoring', False)
    
    def set_input_monitoring(self, value):
        """Set input monitoring state"""
        self._data['input_monitoring'] = value
    
    @property
    def uuid(self):
        """Return track UUID"""
        return self._data.get('uuid', '')
    
    @property
    def output_hardware_device_name(self):
        return self._data.get('output_hardware_device_name', '')
    
    def get_output_hardware_device(self):
        # TODO: Return mock hardware device
        return None
    
    def set_active_ui_notes_monitoring(self):
        """Mock method for UI notes monitoring - does nothing"""
        pass
    
    def all_notes_off(self):
        """Mock method for all notes off - does nothing"""
        pass


class MockSession:
    """Mock session object for testing"""
    
    def __init__(self, session_data, app):
        self._data = session_data
        self._app = app
        
        # Create mock tracks
        self.tracks = []
        for track_data in session_data.get('tracks', []):
            self.tracks.append(MockTrack(track_data, self))
    
    @property
    def name(self):
        return self._data.get('name', '')
    
    @property
    def playing(self):
        return self._data.get('is_playing', False)
    
    @property
    def bpm(self):
        return self._data.get('bpm', 120.0)
    
    @property
    def meter(self):
        return self._data.get('meter', 4)
    
    @property
    def metronome_on(self):
        return self._data.get('metronome_on', False)
    
    @property
    def doing_count_in(self):
        return False  # TODO: Implement count-in
    
    @property
    def playhead_position_in_beats(self):
        return 0.0  # TODO: Get from musical context
    
    @property
    def count_in_playhead_position_in_beats(self):
        return 0.0  # TODO: Implement count-in
    
    def play_stop(self):
        self._app._send_message('/transport/playStop')
    
    def play(self):
        self._app._send_message('/transport/play')
    
    def stop(self):
        self._app._send_message('/transport/stop')
    
    def set_bpm(self, bpm):
        self._app._send_message('/transport/setBpm', [bpm])
    
    def set_meter(self, meter):
        self._app._send_message('/transport/setMeter', [meter])
    
    def metronome_on_off(self):
        self._app._send_message('/metronome/onOff')
    
    def new(self, num_tracks, num_scenes):
        self._app._send_message('/settings/new', [num_tracks, num_scenes])
    
    def scene_play(self, scene_number):
        self._app._send_message('/scene/play', [scene_number])
    
    def scene_duplicate(self, scene_number):
        self._app._send_message('/scene/duplicate', [scene_number])
    
    def get_track_by_idx(self, track_num):
        """Get track by index - mock implementation"""
        if 0 <= track_num < len(self.tracks):
            return self.tracks[track_num]
        return None
    
    def get_clip_by_idx(self, track_num, clip_num):
        """Get clip by track and clip index - mock implementation"""
        track = self.get_track_by_idx(track_num)
        if track and 0 <= clip_num < len(track.clips):
            return track.clips[clip_num]
        return None
    
    @property
    def fixed_length_recording_bars(self):
        return self._data.get('fixed_length_recording_bars', 0)
    
    def set_fix_length_recording_bars(self, bars):
        self._app._send_message('/transport/setFixedLengthRecordingBars', [bars])
    
    @property
    def record_automation_enabled(self):
        return self._data.get('record_automation_enabled', False)
    
    def set_record_automation_enabled(self):
        self._app._send_message('/transport/setRecordAutomationEnabled')
    
    def save(self, slot):
        self._app._send_message('/session/save', [slot])
    
    def load(self, slot):
        self._app._send_message('/session/load', [slot])
    
    def set_fixed_velocity(self, velocity):
        self._app._send_message('/transport/setFixedVelocity', [velocity])
