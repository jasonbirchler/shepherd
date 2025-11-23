"""
WebSocket client for connecting to Shepherd backend
Provides compatibility with existing Push2Controller
"""

import json
import threading
import time
from typing import Optional, Callable
import websocket
import math

# Import real backend classes
from .backend.track import Track


class State:
    """State object that wraps backend state data with hardware device access"""
    
    def __init__(self, state_data):
        self._data = state_data
        self.notes_monitoring_device_name = ""
        self._cached_hardware_devices = {}
    
    def __getattr__(self, name):
        """Allow access to state data attributes"""
        return self._data.get(name)
    
    def _get_hardware_device_from_data(self, name, device_type):
        """Get or create a hardware device wrapper for the given name and type"""
        device_key = f"{device_type}:{name}"
        
        # Return cached device if available
        if device_key in self._cached_hardware_devices:
            return self._cached_hardware_devices[device_key]
        
        # Handle special Push device name mappings
        push_name_mapping = {
            'Push': 'Ableton Push 2 Live Port',
            'PushSimulator': 'Ableton Push 2 Live Port'
        }
        
        # Use mapped name if available
        mapped_name = push_name_mapping.get(name, name)
        
        # Look for device in state data
        if hasattr(self._data, 'hardware_devices'):
            hardware_data = self._data['hardware_devices']
            devices = hardware_data.get('devices', [])
            for device in devices:
                device_name = device.get('midi_device_name', '')
                device_short_name = device.get('short_name', '')
                device_display_name = device.get('name', '')
                
                # Check if any of the device names match (with partial matching for Push)
                if device.get('type') == device_type:
                    if (device_name == mapped_name or device_short_name == mapped_name or 
                        device_display_name == mapped_name or
                        ('Push' in mapped_name and 'Push' in device_name)):
                        # Create a hardware device wrapper
                        wrapper = HardwareDeviceWrapper(device)
                        self._cached_hardware_devices[device_key] = wrapper
                        return wrapper
        
        # If device not found in state data, create a default one
        default_device_data = {
            'type': device_type,
            'name': name,
            'midi_device_name': name,
            'short_name': name
        }
        wrapper = HardwareDeviceWrapper(default_device_data)
        self._cached_hardware_devices[device_key] = wrapper
        return wrapper
    
    def get_input_hardware_device_by_name(self, name):
        """Get input hardware device by name"""
        return self._get_hardware_device_from_data(name, 'input')
    
    def get_output_hardware_device_by_name(self, name):
        """Get output hardware device by name"""
        return self._get_hardware_device_from_data(name, 'output')
    
    def get_available_output_hardware_device_names(self):
        """Get list of available output device names"""
        if hasattr(self._data, 'hardware_devices'):
            return self._data['hardware_devices'].get('available_outputs', [])
        return []
    
    def toggle_shepherd_backend_debug_synth(self):
        """Toggle debug synth - placeholder for now"""
        pass


class HardwareDeviceWrapper:
    """Wrapper for hardware devices that provides the expected interface for MIDI CC values"""
    
    def __init__(self, device_data):
        self._data = device_data
        self._midi_cc_values = {}  # Store current MIDI CC values
        self.midi_channel = 1  # Default MIDI channel
    
    def set_control_change_mapping(self, mapping):
        """Set control change mapping for encoders - mock implementation"""
        # Store mapping for reference if needed
        pass
    
    def get_current_midi_cc_parameter_value(self, cc_number):
        """Get current MIDI CC parameter value"""
        return self._midi_cc_values.get(cc_number, 0)
    
    def set_midi_cc_parameter_value(self, cc_number, value):
        """Set MIDI CC parameter value"""
        # Clamp value to 0-127 range
        value = max(0, min(127, value))
        self._midi_cc_values[cc_number] = value
    
    def send_midi(self, message):
        """Send MIDI message - mock implementation"""
        # This would send MIDI messages to the actual hardware device
        pass
    
    def load_preset(self, bank_num, preset_num):
        """Load preset - mock implementation"""
        # This would load presets on the actual hardware device
        pass
    
    def all_notes_off(self):
        """Send all notes off - mock implementation"""
        # This would send all notes off to the actual hardware device
        pass
    
    def set_notes_mapping(self, mapping):
        """Set notes mapping for pads - mock implementation"""
        # This would set up note mapping for pad functionality
        pass
    
    def set_midi_channel(self, channel):
        """Set MIDI channel for the device"""
        self.midi_channel = channel


class Session:
    """Session object that wraps backend session data with track management"""
    
    def __init__(self, session_data, app):
        self._data = session_data
        self._app = app
        
        # Create tracks from data
        self.tracks = []
        for track_data in session_data.get('tracks', []):
            self.tracks.append(TrackWrapper(track_data, self))
    
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
        """Get track by index"""
        if 0 <= track_num < len(self.tracks):
            return self.tracks[track_num]
        return None
    
    def get_clip_by_idx(self, track_num, clip_num):
        """Get clip by track and clip index"""
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


class TrackWrapper:
    """Wrapper for track data that provides the expected interface"""
    
    def __init__(self, track_data, session):
        self._data = track_data
        self._session = session
        
        # Create clip wrappers
        self.clips = []
        for clip_data in track_data.get('clips', []):
            self.clips.append(ClipWrapper(clip_data, self))
    
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
        """Get the output hardware device for this track"""
        # Get hardware device from the state based on the device name
        if hasattr(self._session._app, 'state') and self._session._app.state:
            return self._session._app.state.get_output_hardware_device_by_name(self.output_hardware_device_name)
        return None
    
    def set_active_ui_notes_monitoring(self):
        """Mock method for UI notes monitoring - does nothing"""
        pass
    
    def all_notes_off(self):
        """Mock method for all notes off - does nothing"""
        pass


class ClipWrapper:
    """Wrapper for clip data that provides the expected interface"""
    
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
        """Toggle recording state"""
        self._data['is_recording'] = not self._data.get('is_recording', False)


class ShepherdConnectionException(Exception):
    """Exception raised when connection to Shepherd backend fails and cannot be re-established"""
    pass


class ShepherdConnectionMonitor(threading.Thread):
    """Thread that monitors WebSocket connection and attempts reconnection when needed"""
    
    def __init__(self, app, initial_delay=2.0, max_delay=30.0, max_attempts=10):
        super().__init__(daemon=True)
        self.app = app
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.should_reconnect = True
        self.connection_lock = threading.Lock()
    
    def run(self):
        """Main reconnection loop"""
        attempt = 0
        delay = self.initial_delay
        
        while self.should_reconnect:
            try:
                # Wait for disconnection
                while self.app.connected:
                    time.sleep(0.5)
                
                attempt += 1
                if attempt > self.max_attempts:
                    print(f"Failed to reconnect after {self.max_attempts} attempts")
                    raise ShepherdConnectionException(
                        f"Failed to connect to Shepherd backend after {self.max_attempts} attempts. "
                        f"Please check that the backend server is running at {self.app.backend_url}"
                    )
                
                print(f"Attempting to reconnect to Shepherd backend (attempt {attempt}/{self.max_attempts})")
                
                with self.connection_lock:
                    # Create new connection
                    self.app._create_new_connection()
                    
                    # Wait for connection to be established
                    timeout = 10  # Wait up to 10 seconds for connection
                    start_time = time.time()
                    while not self.app.connected and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                    
                    if self.app.connected:
                        print("Successfully reconnected to Shepherd backend")
                        attempt = 0  # Reset attempt counter on successful reconnection
                        delay = self.initial_delay  # Reset delay
                        continue
                
                # Connection failed, wait before retry
                print(f"Reconnection attempt {attempt} failed, retrying in {delay} seconds")
                time.sleep(delay)
                
                # Exponential backoff (capped at max_delay)
                delay = min(delay * 1.5, self.max_delay)
                
            except ShepherdConnectionException:
                # Propagate connection exceptions
                raise
            except Exception as e:
                print(f"Unexpected error during reconnection: {e}")
                time.sleep(delay)
    
    def stop(self):
        """Stop the reconnection monitor"""
        self.should_reconnect = False


class ShepherdBackendControllerApp:
    """WebSocket client for connecting to Shepherd backend"""
    
    def __init__(self, backend_host: str = 'localhost', backend_port: int = 9001, 
                 enable_reconnection: bool = True, reconnect_max_attempts: int = 10):
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.backend_url = f"ws://{backend_host}:{backend_port}/shepherd_coms"
        
        # Reconnection configuration
        self.enable_reconnection = enable_reconnection
        self.reconnect_max_attempts = reconnect_max_attempts
        self.connection_monitor: Optional[ShepherdConnectionMonitor] = None
        
        # WebSocket connection
        self.ws: Optional[websocket.WebSocketApp] = None
        self.connected = False
        self.connection_thread: Optional[threading.Thread] = None
        self.connection_lock = threading.Lock()
        
        # State management
        self.state = None
        self.session = None
        
        # Callbacks
        self.on_state_first_synced_callback: Optional[Callable] = None
        self.on_new_session_loaded_callback: Optional[Callable] = None
        self.on_state_update_received_callback: Optional[Callable] = None
        
        # Start connection
        self._connect()
    
    def _connect(self):
        """Connect to the backend WebSocket server"""
        print(f"Connecting to Shepherd backend at {self.backend_url}")
        
        self._create_new_connection()
        
        # Start connection monitor if reconnection is enabled
        if self.enable_reconnection:
            self.connection_monitor = ShepherdConnectionMonitor(
                self, max_attempts=self.reconnect_max_attempts
            )
            self.connection_monitor.start()
    
    def _create_new_connection(self):
        """Create a new WebSocket connection"""
        with self.connection_lock:
            # Close existing connection if any
            if self.ws:
                try:
                    self.ws.close()
                except:
                    pass
            
            # Create new connection
            self.ws = websocket.WebSocketApp(
                self.backend_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start connection in separate thread
            if self.connection_thread and self.connection_thread.is_alive():
                # Don't join the old thread, just let it die as daemon
                pass
            
            self.connection_thread = threading.Thread(
                target=self.ws.run_forever,
                daemon=True
            )
            self.connection_thread.start()
            
            # Reset connection state
            self.connected = False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure proper cleanup"""
        self.disconnect()
    
    def _on_open(self, ws):
        """WebSocket connection opened"""
        print("Connected to Shepherd backend")
        self.connected = True
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            if data.get('type') == 'state_update':
                self._handle_state_update(data.get('data', {}))
            elif data.get('type') == 'error':
                print(f"Backend error: {data.get('message')}")
                
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket error occurred"""
        print(f"WebSocket error: {error}")
        
        # Log different types of errors
        error_str = str(error)
        if "Connection refused" in error_str:
            print("Backend server may be down - will attempt to reconnect")
        elif "Connection aborted" in error_str:
            print("Connection was aborted - will attempt to reconnect")
        elif "SSL" in error_str:
            print("SSL/TLS error - check security settings")
    
    def disconnect(self):
        """Gracefully disconnect and stop reconnection monitoring"""
        print("Disconnecting from Shepherd backend")
        
        # Stop reconnection monitoring
        if self.connection_monitor:
            self.connection_monitor.stop()
            self.connection_monitor = None
        
        # Close WebSocket connection
        with self.connection_lock:
            if self.ws:
                self.ws.close()
                self.ws = None
            self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        print(f"Disconnected from Shepherd backend (code: {close_status_code}, msg: {close_msg})")
        
        with self.connection_lock:
            self.connected = False
        
        # If reconnection is enabled, the connection monitor will handle reconnection
        # If not enabled, this is a permanent disconnection
        if not self.enable_reconnection:
            print("Reconnection disabled - connection permanently lost")
            # You could raise an exception here if you want to fail fast
            # raise ShepherdConnectionException("Connection lost and reconnection is disabled")
    
    def _handle_state_update(self, state_data):
        """Handle state update from backend"""
        first_sync = self.state is None
        
        # Update state
        self.state = State(state_data)
        
        # Update session
        if state_data.get('session'):
            self.session = Session(state_data['session'], self)
        else:
            # Create default session with 1 track if none exists
            default_track = {
                'name': 'Track 1',
                'output_hardware_device_name': 'NTS-1',
                'input_monitoring': True,
                'clips': [],
                'uuid': 'default-track-1'
            }
            self.session = Session({'tracks': [default_track], 'name': 'Default Session'}, self)
        
        # Call callbacks - try both callback attributes and methods
        if first_sync:
            if hasattr(self, 'on_state_first_synced') and callable(getattr(self, 'on_state_first_synced')):
                self.on_state_first_synced()
            elif self.on_state_first_synced_callback:
                self.on_state_first_synced_callback()
            
            # Also call on_full_state_received if it exists (for Push2Controller)
            if hasattr(self, 'on_full_state_received') and callable(getattr(self, 'on_full_state_received')):
                self.on_full_state_received()
        
        if self.session:
            if hasattr(self, 'on_new_session_loaded') and callable(getattr(self, 'on_new_session_loaded')):
                self.on_new_session_loaded()
            elif self.on_new_session_loaded_callback:
                self.on_new_session_loaded_callback()
        
        # Always call state update
        update_data = {
            'updateType': 'propertyChanged',
            'propertyName': 'state',
            'affectedElement': self.state
        }
        
        if hasattr(self, 'on_state_update_received') and callable(getattr(self, 'on_state_update_received')):
            self.on_state_update_received(update_data)
        elif self.on_state_update_received_callback:
            self.on_state_update_received_callback(update_data)
    
    def _send_message(self, address: str, params: list = None):
        """Send message to backend"""
        if not self.connected or not self.ws:
            print(f"Not connected, cannot send: {address}")
            return
        
        if params is None:
            params = []
        
        # Format as OSC-style message
        message = f"{address} {' '.join(map(str, params))}"
        self.ws.send(message)
    
    def sync_session_to_backend(self):
        """Send current session to backend to keep them in sync"""
        if self.session and self.connected:
            try:
                session_data = {
                    'name': self.session.name,
                    'tracks': [{'name': track.name, 'output_hardware_device_name': track.output_hardware_device_name} for track in self.session.tracks],
                    'num_scenes': 4  # Default number of scenes
                }
                # Send JSON as a single message without spaces to avoid splitting
                json_str = json.dumps(session_data, separators=(',', ':'))
                message = f"/session/sync {json_str}"
                if self.connected and self.ws:
                    self.ws.send(message)
                print(f"DEBUG: Sent session sync to backend")
            except Exception as e:
                print(f"ERROR: Failed to sync session to backend: {e}")
    
    # Callback setters for compatibility
    def on_state_first_synced(self):
        """Decorator for state first synced callback"""
        def decorator(func):
            self.on_state_first_synced_callback = func
            return func
        return decorator
    
    def on_new_session_loaded(self):
        """Decorator for new session loaded callback"""
        def decorator(func):
            self.on_new_session_loaded_callback = func
            return func
        return decorator
    
    def on_state_update_received(self):
        """Decorator for state update received callback"""
        def decorator(func):
            self.on_state_update_received_callback = func
            return func
        return decorator


