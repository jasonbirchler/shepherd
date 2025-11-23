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

# Import test fixtures for fallback when backend is unavailable
from .tests.fixtures import MockState, MockSession


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
        self.state = MockState(state_data)
        
        # Update session
        if state_data.get('session'):
            self.session = MockSession(state_data['session'], self)
        else:
            # Create default session with 1 track if none exists
            default_track = {
                'name': 'Track 1',
                'output_hardware_device_name': 'NTS-1',
                'input_monitoring': True,
                'clips': [],
                'uuid': 'default-track-1'
            }
            self.session = MockSession({'tracks': [default_track], 'name': 'Default Session'}, self)
        
        # Call callbacks - try both callback attributes and methods
        if first_sync:
            if hasattr(self, 'on_state_first_synced') and callable(getattr(self, 'on_state_first_synced')):
                self.on_state_first_synced()
            elif self.on_state_first_synced_callback:
                self.on_state_first_synced_callback()
            
            # Also call on_full_state_received if it exists (for Push2Controller)
            print(f"Client: Checking for on_full_state_received callback...")
            if hasattr(self, 'on_full_state_received') and callable(getattr(self, 'on_full_state_received')):
                print("Client: Calling on_full_state_received...")
                self.on_full_state_received()
            else:
                print("Client: on_full_state_received not found or not callable")
        
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


