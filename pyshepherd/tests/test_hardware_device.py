import pytest
from unittest.mock import Mock, patch, MagicMock
from pyshepherd.backend import HardwareDevice, HardwareDeviceManager


class TestHardwareDevice:
    """Test suite for HardwareDevice functionality"""
    
    def test_hardware_device_creation(self):
        """Test hardware device creation"""
        device = HardwareDevice(
            name="Test Synth",
            short_name="Synth1",
            device_type="output",
            midi_device_name="USB MIDI Device",
            midi_channel=5
        )
        
        assert device.name == "Test Synth"
        assert device.short_name == "Synth1"
        assert device.type == "output"
        assert device.midi_device_name == "USB MIDI Device"
        assert device.midi_channel == 5
        assert device.is_open == False
        assert device.uuid is not None
    
    def test_device_type_checking(self):
        """Test device type checking methods"""
        output_device = HardwareDevice("Out", "Out1", "output", "MIDI Out", 1)
        input_device = HardwareDevice("In", "In1", "input", "MIDI In", 1)
        
        assert output_device.is_type_output() == True
        assert output_device.is_type_input() == False
        
        assert input_device.is_type_output() == False
        assert input_device.is_type_input() == True
    
    @patch('mido.open_output')
    def test_output_device_open_close(self, mock_open_output):
        """Test opening and closing output device"""
        mock_port = Mock()
        mock_open_output.return_value = mock_port
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 1)
        
        # Open device
        result = device.open()
        assert result == True
        assert device.is_open == True
        mock_open_output.assert_called_once_with("MIDI Out")
        
        # Close device
        device.close()
        assert device.is_open == False
        mock_port.close.assert_called_once()
    
    @patch('mido.open_input')
    def test_input_device_open_close(self, mock_open_input):
        """Test opening and closing input device"""
        mock_port = Mock()
        mock_open_input.return_value = mock_port
        
        device = HardwareDevice("Test", "Test1", "input", "MIDI In", 1)
        
        # Open device
        result = device.open()
        assert result == True
        assert device.is_open == True
        mock_open_input.assert_called_once_with("MIDI In")
        
        # Close device
        device.close()
        assert device.is_open == False
        mock_port.close.assert_called_once()
    
    @patch('mido.open_output')
    def test_device_open_failure(self, mock_open_output):
        """Test device open failure handling"""
        mock_open_output.side_effect = Exception("Device not found")
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 1)
        
        result = device.open()
        assert result == False
        assert device.is_open == False
    
    @patch('mido.open_output')
    def test_send_midi_message(self, mock_open_output):
        """Test sending MIDI messages"""
        mock_port = Mock()
        mock_open_output.return_value = mock_port
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 5)
        device.open()
        
        # Create mock message
        mock_message = Mock()
        mock_message.channel = None
        mock_message.copy.return_value = Mock()
        
        # Send message
        device.send_message(mock_message)
        
        # Should set channel and send
        mock_message.copy.assert_called_once_with(channel=4)  # 5-1 for mido
        mock_port.send.assert_called_once()
    
    @patch('mido.open_input')
    def test_receive_midi_messages(self, mock_open_input):
        """Test receiving MIDI messages"""
        mock_port = Mock()
        mock_messages = [Mock(), Mock(), Mock()]
        mock_port.iter_pending.return_value = mock_messages
        mock_open_input.return_value = mock_port
        
        device = HardwareDevice("Test", "Test1", "input", "MIDI In", 1)
        device.open()
        
        # Receive messages
        messages = device.receive_messages()
        
        assert len(messages) == 3
        assert messages == mock_messages
        mock_port.iter_pending.assert_called_once()
    
    def test_device_serialization(self):
        """Test device to_dict conversion"""
        device = HardwareDevice("Test Synth", "Synth1", "output", "USB MIDI", 3)
        
        data = device.to_dict()
        
        assert data['name'] == "Test Synth"
        assert data['short_name'] == "Synth1"
        assert data['type'] == "output"
        assert data['midi_device_name'] == "USB MIDI"
        assert data['midi_channel'] == 3
        assert data['is_open'] == False
        assert 'uuid' in data


class TestHardwareDeviceManager:
    """Test suite for HardwareDeviceManager functionality"""
    
    def test_device_manager_initialization(self):
        """Test device manager creation"""
        manager = HardwareDeviceManager()
        
        assert len(manager.devices) == 0
        assert manager._available_inputs == []
        assert manager._available_outputs == []
    
    @patch('mido.get_output_names')
    @patch('mido.get_input_names')
    def test_scan_available_devices(self, mock_inputs, mock_outputs):
        """Test scanning for available MIDI devices"""
        mock_outputs.return_value = ['MIDI Out 1', 'MIDI Out 2']
        mock_inputs.return_value = ['MIDI In 1']
        
        manager = HardwareDeviceManager()
        manager._scan_available_devices()
        
        assert manager._available_outputs == ['MIDI Out 1', 'MIDI Out 2']
        assert manager._available_inputs == ['MIDI In 1']
    
    @patch('mido.get_output_names')
    @patch('mido.get_input_names')
    @patch('mido.open_output')
    @patch('mido.open_input')
    def test_initialize_with_devices(self, mock_open_input, mock_open_output, mock_inputs, mock_outputs):
        """Test initialization with automatic device creation"""
        mock_outputs.return_value = ['Synth 1', 'Synth 2']
        mock_inputs.return_value = ['Controller 1']
        mock_open_output.return_value = Mock()
        mock_open_input.return_value = Mock()
        
        manager = HardwareDeviceManager()
        manager.initialize()
        
        # Should create devices for all available ports
        assert len(manager.devices) == 3
        
        output_devices = manager.get_output_devices()
        input_devices = manager.get_input_devices()
        
        assert len(output_devices) == 2
        assert len(input_devices) == 1
    
    def test_add_remove_device(self):
        """Test adding and removing devices"""
        manager = HardwareDeviceManager()
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 1)
        device.open = Mock(return_value=True)
        
        # Add device
        manager.add_device(device)
        assert len(manager.devices) == 1
        assert device in manager.devices
        device.open.assert_called_once()
        
        # Remove device
        device.close = Mock()
        manager.remove_device(device.uuid)
        assert len(manager.devices) == 0
        device.close.assert_called_once()
    
    def test_get_device_by_name(self):
        """Test device retrieval by name"""
        manager = HardwareDeviceManager()
        
        device1 = HardwareDevice("Device 1", "Dev1", "output", "MIDI Out 1", 1)
        device2 = HardwareDevice("Device 2", "Dev2", "input", "MIDI In 1", 1)
        
        device1.open = Mock(return_value=True)
        device2.open = Mock(return_value=True)
        
        manager.add_device(device1)
        manager.add_device(device2)
        
        # Find by full name
        found = manager.get_device_by_name("Device 1")
        assert found == device1
        
        # Find by short name
        found = manager.get_device_by_name("Dev2")
        assert found == device2
        
        # Not found
        found = manager.get_device_by_name("NonExistent")
        assert found is None
    
    def test_get_device_by_uuid(self):
        """Test device retrieval by UUID"""
        manager = HardwareDeviceManager()
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 1)
        device.open = Mock(return_value=True)
        manager.add_device(device)
        
        # Find by UUID
        found = manager.get_device_by_uuid(device.uuid)
        assert found == device
        
        # Not found
        found = manager.get_device_by_uuid("invalid-uuid")
        assert found is None
    
    def test_get_typed_devices(self):
        """Test getting devices by type"""
        manager = HardwareDeviceManager()
        
        output_device = HardwareDevice("Out", "Out1", "output", "MIDI Out", 1)
        input_device = HardwareDevice("In", "In1", "input", "MIDI In", 1)
        
        output_device.open = Mock(return_value=True)
        input_device.open = Mock(return_value=True)
        
        manager.add_device(output_device)
        manager.add_device(input_device)
        
        # Get output device
        found = manager.get_output_device("Out1")
        assert found == output_device
        
        # Get input device
        found = manager.get_input_device("In1")
        assert found == input_device
        
        # Wrong type should return None
        found = manager.get_output_device("In1")
        assert found is None
        
        found = manager.get_input_device("Out1")
        assert found is None
    
    def test_get_device_lists(self):
        """Test getting lists of devices by type"""
        manager = HardwareDeviceManager()
        
        output1 = HardwareDevice("Out1", "Out1", "output", "MIDI Out 1", 1)
        output2 = HardwareDevice("Out2", "Out2", "output", "MIDI Out 2", 1)
        input1 = HardwareDevice("In1", "In1", "input", "MIDI In 1", 1)
        
        for device in [output1, output2, input1]:
            device.open = Mock(return_value=True)
            manager.add_device(device)
        
        # Get device lists
        outputs = manager.get_output_devices()
        inputs = manager.get_input_devices()
        
        assert len(outputs) == 2
        assert len(inputs) == 1
        assert output1 in outputs
        assert output2 in outputs
        assert input1 in inputs
    
    def test_get_available_names(self):
        """Test getting available device names"""
        manager = HardwareDeviceManager()
        
        output1 = HardwareDevice("Out1", "Out1", "output", "MIDI Out 1", 1)
        output2 = HardwareDevice("Out2", "Out2", "output", "MIDI Out 2", 1)
        input1 = HardwareDevice("In1", "In1", "input", "MIDI In 1", 1)
        
        for device in [output1, output2, input1]:
            device.open = Mock(return_value=True)
            manager.add_device(device)
        
        # Get name lists
        output_names = manager.get_available_output_names()
        input_names = manager.get_available_input_names()
        
        assert output_names == ["Out1", "Out2"]
        assert input_names == ["In1"]
    
    def test_close_all_devices(self):
        """Test closing all devices"""
        manager = HardwareDeviceManager()
        
        device1 = HardwareDevice("Dev1", "Dev1", "output", "MIDI Out", 1)
        device2 = HardwareDevice("Dev2", "Dev2", "input", "MIDI In", 1)
        
        device1.open = Mock(return_value=True)
        device2.open = Mock(return_value=True)
        device1.close = Mock()
        device2.close = Mock()
        
        manager.add_device(device1)
        manager.add_device(device2)
        
        # Close all
        manager.close_all_devices()
        
        device1.close.assert_called_once()
        device2.close.assert_called_once()
    
    def test_manager_serialization(self):
        """Test manager to_dict conversion"""
        manager = HardwareDeviceManager()
        manager._available_outputs = ['Out1', 'Out2']
        manager._available_inputs = ['In1']
        
        device = HardwareDevice("Test", "Test1", "output", "MIDI Out", 1)
        device.open = Mock(return_value=True)
        manager.add_device(device)
        
        data = manager.to_dict()
        
        assert data['available_outputs'] == ['Out1', 'Out2']
        assert data['available_inputs'] == ['In1']
        assert len(data['devices']) == 1
        assert data['devices'][0]['name'] == "Test"