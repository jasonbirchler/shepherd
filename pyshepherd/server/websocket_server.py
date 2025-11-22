import asyncio
import websockets
import json
import threading
from typing import Set, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..backend.sequencer import Sequencer


class WebSocketServer:
    """WebSocket server for remote control of Shepherd backend"""
    
    def __init__(self, sequencer: 'Sequencer', host: str = 'localhost', port: int = 9001):
        self.sequencer = sequencer
        self.host = host
        self.port = port
        
        # Connected clients
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Server state
        self.server = None
        self.is_running = False
        self._server_thread: threading.Thread = None
    
    def start(self):
        """Start the WebSocket server in a separate thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
    
    def stop(self):
        """Stop the WebSocket server"""
        self.is_running = False
        if self.server:
            self.server.close()
    
    def _run_server(self):
        """Run the WebSocket server event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._start_server())
        except Exception as e:
            print(f"WebSocket server error: {e}")
        finally:
            loop.close()
    
    async def _start_server(self):
        """Start the WebSocket server"""
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        
        # Keep server running
        await self.server.wait_closed()
    
    async def _handle_client(self, websocket, path):
        """Handle a new WebSocket client connection"""
        print(f"Client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            # Send initial state
            await self._send_state_update(websocket)
            
            # Handle incoming messages
            async for message in websocket:
                await self._handle_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {websocket.remote_address}")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def _handle_message(self, websocket, message: str):
        """Handle incoming WebSocket message"""
        try:
            # Parse OSC-style message format: "/address param1 param2 ..."
            parts = message.strip().split()
            if not parts:
                return
            
            address = parts[0]
            params = parts[1:] if len(parts) > 1 else []
            
            # Route message to appropriate handler
            await self._route_message(websocket, address, params)
            
        except Exception as e:
            print(f"Error handling message '{message}': {e}")
            await self._send_error(websocket, str(e))
    
    async def _route_message(self, websocket, address: str, params: list):
        """Route message to appropriate handler based on address"""
        
        # Session management
        if address == '/settings/new':
            num_tracks, num_scenes = int(params[0]), int(params[1])
            self.sequencer.new_session(num_tracks, num_scenes)
        
        elif address == '/settings/save':
            filepath = params[0] if params else 'session.json'
            self.sequencer.save_session(filepath)
        
        elif address == '/settings/load':
            filepath = params[0] if params else 'session.json'
            self.sequencer.load_session(filepath)
        
        # Transport controls
        elif address == '/transport/play':
            if self.sequencer.session:
                self.sequencer.session.play()
        
        elif address == '/transport/stop':
            if self.sequencer.session:
                self.sequencer.session.stop()
        
        elif address == '/transport/playStop':
            if self.sequencer.session:
                self.sequencer.session.play_stop_toggle()
        
        elif address == '/transport/setBpm':
            bpm = float(params[0])
            if self.sequencer.session:
                self.sequencer.session.set_bpm(bpm)
        
        elif address == '/transport/setMeter':
            meter = int(params[0])
            if self.sequencer.session:
                self.sequencer.session.set_meter(meter)
        
        # Metronome
        elif address == '/metronome/onOff':
            if self.sequencer.session:
                current = self.sequencer.session.metronome_on
                self.sequencer.session.set_metronome(not current)
        
        # Scene controls
        elif address == '/scene/play':
            scene_idx = int(params[0])
            if self.sequencer.session:
                self.sequencer.session.play_scene(scene_idx)
        
        # Track controls
        elif address == '/track/setOutputHardwareDevice':
            track_uuid, device_name = params[0], params[1]
            # TODO: Implement track device assignment
        
        # Clip controls
        elif address.startswith('/clip/'):
            # TODO: Implement clip controls
            pass
        
        # Send state update after processing
        await self._broadcast_state_update()
    
    async def _send_state_update(self, websocket=None):
        """Send current state to client(s)"""
        state = self.sequencer.get_state_dict()
        message = json.dumps({
            'type': 'state_update',
            'data': state
        })
        
        if websocket:
            await websocket.send(message)
        else:
            await self._broadcast(message)
    
    async def _broadcast_state_update(self):
        """Broadcast state update to all clients"""
        await self._send_state_update()
    
    async def _send_error(self, websocket, error_message: str):
        """Send error message to client"""
        message = json.dumps({
            'type': 'error',
            'message': error_message
        })
        await websocket.send(message)
    
    async def _broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        # Send to all clients, remove disconnected ones
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    def broadcast_state_update_sync(self):
        """Synchronous wrapper for broadcasting state updates"""
        if self.is_running and self.clients:
            # Schedule the coroutine in the server's event loop
            # This is called from the main sequencer thread
            pass  # TODO: Implement thread-safe state broadcasting