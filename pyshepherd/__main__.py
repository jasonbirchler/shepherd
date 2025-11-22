#!/usr/bin/env python3
"""
Shepherd Backend - Standalone Application

Run pyshepherd as a standalone MIDI sequencer backend:
    python -m pyshepherd

Options:
    --host HOST         WebSocket server host (default: localhost)
    --port PORT         WebSocket server port (default: 9001)  
    --no-websocket      Disable WebSocket server
    --sample-rate RATE  Audio sample rate (default: 44100)
    --buffer-size SIZE  Audio buffer size (default: 512)
"""

import argparse
import signal
import sys
import time
from .backend import Sequencer


def main():
    parser = argparse.ArgumentParser(description='Shepherd MIDI Sequencer Backend')
    parser.add_argument('--host', default='localhost', help='WebSocket server host')
    parser.add_argument('--port', type=int, default=9001, help='WebSocket server port')
    parser.add_argument('--no-websocket', action='store_true', help='Disable WebSocket server')
    parser.add_argument('--sample-rate', type=float, default=44100.0, help='Audio sample rate')
    parser.add_argument('--buffer-size', type=int, default=512, help='Audio buffer size')
    
    args = parser.parse_args()
    
    print("Starting Shepherd Backend...")
    print(f"Sample Rate: {args.sample_rate} Hz")
    print(f"Buffer Size: {args.buffer_size} samples")
    
    # Create sequencer
    sequencer = Sequencer(
        enable_websocket=not args.no_websocket,
        websocket_port=args.port
    )
    
    # Prepare with audio settings
    sequencer.prepare(
        sample_rate=args.sample_rate,
        samples_per_slice=args.buffer_size
    )
    
    if not args.no_websocket:
        print(f"WebSocket Server: ws://{args.host}:{args.port}")
    
    # Start sequencer
    sequencer.start()
    print("Shepherd Backend started. Press Ctrl+C to stop.")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down Shepherd Backend...")
        sequencer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == '__main__':
    main()