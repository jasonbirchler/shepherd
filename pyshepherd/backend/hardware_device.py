import mido
from typing import Dict, List, Optional, Any
import uuid


class HardwareDevice:
    """Represents a MIDI hardware device (input or output)"""
    
    def __init__(self, name: str, short_name: str, device_type: str,
                 midi_device_name: str, midi_channel: int = 1):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.short_name = short_name
        self.type = device_type  # 'input' or 'output'
        self.midi_device_name = midi_device_name
        self.midi_channel = midi_channel
        
        # MIDI CC mapping and values
        self._control_change_mapping: Dict[int, int] = {}  # Maps encoder numbers to CC numbers
        self._midi_cc_values: Dict[int, int] = {}  # Current CC values
        
        # MIDI port
        self._midi_port: Optional[mido.ports.BasePort] = None
        self.is_open = False
    
    def open(self) -> bool:
        """Open the MIDI device"""
        try:
            if self.type == 'output':
                self._midi_port = mido.open_output(self.midi_device_name)
            else:
                self._midi_port = mido.open_input(self.midi_device_name)
            self.is_open = True
            return True
        except Exception as e:
            print(f"Failed to open MIDI device {self.midi_device_name}: {e}")
            return False
    
    def close(self):
        """Close the MIDI device"""
        if self._midi_port:
            self._midi_port.close()
            self._midi_port = None
        self.is_open = False
    
    def send_message(self, message: mido.Message):
        """Send MIDI message (output devices only)"""
        if self.type == 'output' and self.is_open and self._midi_port:
            try:
                # Set channel if not already set
                if hasattr(message, 'channel') and message.channel is None:
                    message = message.copy(channel=self.midi_channel - 1)  # mido uses 0-15
                self._midi_port.send(message)
            except Exception as e:
                print(f"Failed to send MIDI message to {self.name}: {e}")
    
    def receive_messages(self) -> List[mido.Message]:
        """Receive MIDI messages (input devices only)"""
        messages = []
        if self.type == 'input' and self.is_open and self._midi_port:
            try:
                # Get all pending messages
                for message in self._midi_port.iter_pending():
                    messages.append(message)
            except Exception as e:
                print(f"Failed to receive MIDI messages from {self.name}: {e}")
        return messages
    
    def is_type_output(self) -> bool:
        """Check if this is an output device"""
        return self.type == 'output'
    
    def is_type_input(self) -> bool:
        """Check if this is an input device"""
        return self.type == 'input'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'short_name': self.short_name,
            'type': self.type,
            'midi_device_name': self.midi_device_name,
            'midi_channel': self.midi_channel,
            'is_open': self.is_open
        }
    
    def set_control_change_mapping(self, mapping: List[int]):
        """Set control change mapping for encoders
        
        Args:
            mapping: List of 128 integers where index is encoder number and value is CC number
                    Use -1 to disable an encoder
        """
        self._control_change_mapping = {}
        for encoder_num, cc_number in enumerate(mapping):
            if cc_number >= 0:  # Only map enabled encoders
                self._control_change_mapping[encoder_num] = cc_number
    
    def get_current_midi_cc_parameter_value(self, cc_number: int) -> int:
        """Get current value of a MIDI CC parameter"""
        return self._midi_cc_values.get(cc_number, 0)
    
    def set_midi_cc_parameter_value(self, cc_number: int, value: int):
        """Set MIDI CC parameter value and send MIDI CC message if output device"""
        # Clamp value to 0-127 range
        value = max(0, min(127, value))
        self._midi_cc_values[cc_number] = value
        
        # Send MIDI CC message if this is an output device
        if self.type == 'output':
            cc_message = mido.Message('control_change',
                                     channel=self.midi_channel - 1,
                                     control=cc_number,
                                     value=value)
            self.send_message(cc_message)
    
    def handle_control_change(self, cc_number: int, value: int):
        """Handle incoming control change message"""
        self._midi_cc_values[cc_number] = value


class HardwareDeviceManager:
    """Manages MIDI hardware devices"""
    
    def __init__(self):
        self.devices: List[HardwareDevice] = []
        self._available_inputs: List[str] = []
        self._available_outputs: List[str] = []
    
    def initialize(self):
        """Initialize and scan for available MIDI devices"""
        self._scan_available_devices()
        self._load_device_configuration()
    
    def _scan_available_devices(self):
        """Scan for available MIDI input/output devices"""
        try:
            self._available_inputs = mido.get_input_names()
            self._available_outputs = mido.get_output_names()
        except Exception as e:
            print(f"Failed to scan MIDI devices: {e}")
            self._available_inputs = []
            self._available_outputs = []
    
    def _load_device_configuration(self):
        """Load hardware device configuration from file"""
        # TODO: Load from hardwareDevices.json
        # For now, create devices for all available MIDI ports
        
        # Create output devices
        for i, output_name in enumerate(self._available_outputs):
            device = HardwareDevice(
                name=f"Output {i+1}",
                short_name=f"Out{i+1}",
                device_type='output',
                midi_device_name=output_name,
                midi_channel=1
            )
            self.add_device(device)
        
        # Create input devices
        for i, input_name in enumerate(self._available_inputs):
            device = HardwareDevice(
                name=f"Input {i+1}",
                short_name=f"In{i+1}",
                device_type='input',
                midi_device_name=input_name,
                midi_channel=1
            )
            self.add_device(device)
    
    def add_device(self, device: HardwareDevice):
        """Add a hardware device"""
        self.devices.append(device)
        device.open()  # Try to open immediately
    
    def remove_device(self, device_uuid: str):
        """Remove a hardware device"""
        device = self.get_device_by_uuid(device_uuid)
        if device:
            device.close()
            self.devices = [d for d in self.devices if d.uuid != device_uuid]
    
    def get_device_by_name(self, name: str) -> Optional[HardwareDevice]:
        """Get device by name or short name"""
        for device in self.devices:
            if device.name == name or device.short_name == name:
                return device
        return None
    
    def get_device_by_uuid(self, device_uuid: str) -> Optional[HardwareDevice]:
        """Get device by UUID"""
        for device in self.devices:
            if device.uuid == device_uuid:
                return device
        return None
    
    def get_output_device(self, name: str) -> Optional[HardwareDevice]:
        """Get output device by name"""
        device = self.get_device_by_name(name)
        if device and device.is_type_output():
            return device
        return None
    
    def get_input_device(self, name: str) -> Optional[HardwareDevice]:
        """Get input device by name"""
        device = self.get_device_by_name(name)
        if device and device.is_type_input():
            return device
        return None
    
    def get_output_devices(self) -> List[HardwareDevice]:
        """Get all output devices"""
        return [d for d in self.devices if d.is_type_output()]
    
    def get_input_devices(self) -> List[HardwareDevice]:
        """Get all input devices"""
        return [d for d in self.devices if d.is_type_input()]
    
    def get_available_output_names(self) -> List[str]:
        """Get names of available output devices"""
        return [d.short_name for d in self.get_output_devices()]
    
    def get_available_input_names(self) -> List[str]:
        """Get names of available input devices"""
        return [d.short_name for d in self.get_input_devices()]
    
    def close_all_devices(self):
        """Close all MIDI devices"""
        for device in self.devices:
            device.close()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'devices': [device.to_dict() for device in self.devices],
            'available_inputs': self._available_inputs,
            'available_outputs': self._available_outputs
        }
