import definitions
import push2_python
import math

from definitions import ShepherdControllerMode
from utils import show_text, draw_knob


class MIDICCControl(object):

    color = definitions.GRAY_LIGHT
    color_rgb = None
    name = 'Unknown'
    section = 'unknown'
    cc_number = 10  # 0-127
    vmin = 0
    vmax = 127
    get_color_func = None
    value_labels_map = {}

    def __init__(self, cc_number, name, section_name, get_color_func):
        self.cc_number = cc_number
        self.name = name
        self.section = section_name
        self.get_color_func = get_color_func

    def draw(self, ctx, x_part, value):
        draw_knob(ctx,
                  x_part,
                  self.name,
                  value,
                  self.vmin,
                  self.vmax,
                  self.value_labels_map.get(str(value), str(value)),
                  self.get_color_func(),
                  margin_top=25)


class MIDICCMode(ShepherdControllerMode):

    midi_cc_button_names = [
        push2_python.constants.BUTTON_UPPER_ROW_1,
        push2_python.constants.BUTTON_UPPER_ROW_2,
        push2_python.constants.BUTTON_UPPER_ROW_3,
        push2_python.constants.BUTTON_UPPER_ROW_4,
        push2_python.constants.BUTTON_UPPER_ROW_5,
        push2_python.constants.BUTTON_UPPER_ROW_6,
        push2_python.constants.BUTTON_UPPER_ROW_7,
        push2_python.constants.BUTTON_UPPER_ROW_8
    ]
    page_left_button = push2_python.constants.BUTTON_PAGE_LEFT
    page_right_button = push2_python.constants.BUTTON_PAGE_RIGHT

    buttons_used = midi_cc_button_names + [page_left_button, page_right_button]

    device_midi_control_ccs = {}
    active_midi_control_ccs = []
    current_selected_section_and_page = {}

    def initialize(self, settings=None):
        print('Initializing MIDI CC mappings...')
        for device_short_name in self.get_all_distinct_device_short_names_helper():
            try:
                midi_cc = self.app.track_selection_mode.devices_info[device_short_name]['midi_cc']
            except KeyError:
                midi_cc = None
            
            if midi_cc is not None:
                # Create MIDI CC mappings for devices with definitions
                self.device_midi_control_ccs[device_short_name] = []
                for section in midi_cc:
                    section_name = section['section']
                    for name, cc_number in section['controls'].items():
                        control = MIDICCControl(cc_number, name, section_name, self.get_current_track_color_helper)
                        if section.get('control_value_label_maps', {}).get(name, False):
                            control.value_labels_map = section['control_value_label_maps'][name]
                        self.device_midi_control_ccs[device_short_name].append(control)
                print('- Loaded {0} MIDI cc mappings for {1}'.format(len(self.device_midi_control_ccs[device_short_name]), device_short_name))
            else:
                # No definition file for device exists, or no midi CC were defined for that device
                self.device_midi_control_ccs[device_short_name] = []
                for i in range(0, 128):
                    section_s = (i // 16) * 16
                    section_e = section_s + 15
                    control = MIDICCControl(i, 'CC {0}'.format(i), '{0} to {1}'.format(section_s, section_e), self.get_current_track_color_helper)
                    self.device_midi_control_ccs[device_short_name].append(control)
                print('- Loaded default MIDI cc mappings for {0}'.format(device_short_name))
      
        # Fill in current page and section variables
        for device_short_name in self.device_midi_control_ccs:
            self.current_selected_section_and_page[device_short_name] = (self.device_midi_control_ccs[device_short_name][0].section, 0)

    def get_all_distinct_device_short_names_helper(self):
        return self.app.track_selection_mode.get_all_distinct_device_short_names()

    def get_current_track_color_helper(self):
        return self.app.track_selection_mode.get_current_track_color()

    def get_current_track_device_short_name_helper(self):
        return self.app.track_selection_mode.get_current_track_device_short_name()

    def get_current_track_midi_cc_sections(self):
        section_names = []
        for control in self.device_midi_control_ccs.get(self.get_current_track_device_short_name_helper(), []):
            section_name = control.section
            if section_name not in section_names:
                section_names.append(section_name)
        return section_names

    def get_currently_selected_midi_cc_section_and_page(self):
        device_short_name = self.get_current_track_device_short_name_helper()
        if device_short_name not in self.current_selected_section_and_page:
            # Initialize with first section if not already set
            controls = self.device_midi_control_ccs.get(device_short_name, [])
            if controls:
                first_section = controls[0].section
                self.current_selected_section_and_page[device_short_name] = (first_section, 0)
            else:
                return ('', 0)
        return self.current_selected_section_and_page.get(device_short_name, ('', 0))

    def get_midi_cc_controls_for_current_track_and_section(self):
        section, _ = self.get_currently_selected_midi_cc_section_and_page()
        return [control for control in self.device_midi_control_ccs.get(self.get_current_track_device_short_name_helper(), []) if control.section == section]

    def get_midi_cc_controls_for_current_track_section_and_page(self):
        all_section_controls = self.get_midi_cc_controls_for_current_track_and_section()
        _, page = self.get_currently_selected_midi_cc_section_and_page()
        try:
            return all_section_controls[page * 8:(page+1) * 8]
        except IndexError:
            return []

    def update_current_section_page(self, new_section=None, new_page=None):
        current_section, current_page = self.get_currently_selected_midi_cc_section_and_page()
        result = [current_section, current_page]
        if new_section is not None:
            result[0] = new_section
        if new_page is not None:
            result[1] = new_page
        self.current_selected_section_and_page[self.get_current_track_device_short_name_helper()] = result
        self.active_midi_control_ccs = self.get_midi_cc_controls_for_current_track_section_and_page()
        self.app.buttons_need_update = True
        self.update_encoders_backend_mapping()

    def get_should_show_midi_cc_next_prev_pages_for_section(self):
        all_section_controls = self.get_midi_cc_controls_for_current_track_and_section()
        _, page = self.get_currently_selected_midi_cc_section_and_page()
        show_prev = False
        if page > 0:
            show_prev = True
        show_next = False
        if (page + 1) * 8 < len(all_section_controls):
            show_next = True
        return show_prev, show_next

    def new_track_selected(self):
        device_short_name = self.get_current_track_device_short_name_helper()
        # Initialize section/page for this device if not already set
        if device_short_name not in self.current_selected_section_and_page:
            controls = self.device_midi_control_ccs.get(device_short_name, [])
            if controls:
                first_section = controls[0].section
                self.current_selected_section_and_page[device_short_name] = (first_section, 0)
        self.active_midi_control_ccs = self.get_midi_cc_controls_for_current_track_section_and_page()
        self.update_encoders_backend_mapping()

    def update_encoders_backend_mapping(self):
        # Update backend mapping of "Push" input device
        topPushEncoders = []
        for encoder_num in range(0, 8):
            try:
                topPushEncoders.append(self.active_midi_control_ccs[encoder_num].cc_number)
            except IndexError:
                topPushEncoders.append(-1)

        mapping = [-1 for i in range(0, 128)]
        mapping[1] = 1  # Always allow modulation wheel
        mapping[64] = 64  # Always allow sustain pedal
        mapping[71:71+8] = topPushEncoders
        device = self.state.get_input_hardware_device_by_name("PushSimulator" if self.app.using_push_simulator else "Push")
        if device is not None:
            device.set_control_change_mapping(mapping)

    def clear_encoders_backend_mapping(self):
        device = self.state.get_input_hardware_device_by_name("PushSimulator" if self.app.using_push_simulator else "Push")
        if device is not None:
            device.set_control_change_mapping([-1 for i in range(0, 128)])

    def activate(self):
        self.update_buttons()
        self.update_encoders_backend_mapping()

    def deactivate(self):
        # Run supperclass deactivate to set all used buttons to black
        super().deactivate()
        # Clear encoders mapping in backend
        self.clear_encoders_backend_mapping()

    def update_buttons(self):
        n_midi_cc_sections = len(self.get_current_track_midi_cc_sections())
        for count, name in enumerate(self.midi_cc_button_names):
            self.set_button_color_if_expression(name, count < n_midi_cc_sections, false_color=definitions.BLACK)

        show_prev, show_next = self.get_should_show_midi_cc_next_prev_pages_for_section()
        self.set_button_color_if_expression(self.page_left_button, show_prev)
        self.set_button_color_if_expression(self.page_right_button, show_next)

    def update_display(self, ctx, w, h):
        # Fixed rendering - text overflow was the issue!
        
        if not self.app.is_mode_active(self.app.settings_mode) and not self.app.is_mode_active(self.app.clip_triggering_mode) and not self.app.is_mode_active(self.app.clip_edit_mode):
            # If settings mode is active, don't draw the upper parts of the screen because settings page will
            # "cover them"

            # Draw MIDI CCs section names (shortened to prevent overflow)
            section_names = self.get_current_track_midi_cc_sections()[0:8]
            if section_names:
                height = 20
                for i, section_name in enumerate(section_names):
                    is_selected = False
                    selected_section, _ = self.get_currently_selected_midi_cc_section_and_page()
                    if selected_section == section_name:
                        is_selected = True

                    current_track_color = self.get_current_track_color_helper()
                    if is_selected:
                        background_color = current_track_color
                        font_color = definitions.BLACK
                    else:
                        background_color = definitions.BLACK
                        font_color = current_track_color
                    
                    # Shorten section name to prevent overflow (e.g., "0 to 15" -> "0")
                    short_name = section_name.split(' ')[0] if ' ' in section_name else section_name
                    show_text(ctx, i, 0, short_name, height=height,
                            font_color=font_color, background_color=background_color)

            # Draw MIDI CC controls
            if self.active_midi_control_ccs:
                for i in range(0, min(len(self.active_midi_control_ccs), 8)):
                    hardware_device = \
                        self.state.get_output_hardware_device_by_name(self.get_current_track_device_short_name_helper())
                    if hardware_device is not None:
                        value = hardware_device.get_current_midi_cc_parameter_value(
                            self.active_midi_control_ccs[i].cc_number)
                        self.active_midi_control_ccs[i].draw(ctx, i, value)
                    else:
                        continue

        # Always draw track names at the bottom (similar to track selection mode)
        if self.session is not None and self.session.tracks is not None:
            height = 20
            for i in range(0, len(self.session.tracks)):
                track_color = self.app.track_selection_mode.get_track_color(self.session.tracks[i])
                if self.app.track_selection_mode.selected_track == i:
                    background_color = track_color
                    font_color = definitions.BLACK
                else:
                    background_color = definitions.BLACK
                    font_color = track_color
                track = self.session.get_track_by_idx(i)
                device_short_name = track.output_hardware_device_name
                if track.input_monitoring:
                    device_short_name = '+' + device_short_name
                # Show placeholder text only if device name is completely empty (no plus added)
                if not device_short_name or device_short_name == '+':
                    device_short_name = f'Track {i+1}'
                show_text(ctx, i, h - height, device_short_name, height=height,
                        font_color=font_color, background_color=background_color)

    def on_button_pressed(self, button_name, shift=False, select=False, long_press=False, double_press=False):
        if button_name in self.midi_cc_button_names:
            current_track_sections = self.get_current_track_midi_cc_sections()
            n_sections = len(current_track_sections)
            idx = self.midi_cc_button_names.index(button_name)
            if idx < n_sections:
                new_section = current_track_sections[idx]
                self.update_current_section_page(new_section=new_section, new_page=0)
            return True

        elif button_name in [self.page_left_button, self.page_right_button]:
            show_prev, show_next = self.get_should_show_midi_cc_next_prev_pages_for_section()
            _, current_page = self.get_currently_selected_midi_cc_section_and_page()
            if button_name == self.page_left_button and show_prev:
                self.update_current_section_page(new_page=current_page - 1)
            elif button_name == self.page_right_button and show_next:
                self.update_current_section_page(new_page=current_page + 1)
            return True

    def on_encoder_rotated(self, encoder_name, increment):
        if not self.app.is_mode_active(self.app.settings_mode) and not self.app.is_mode_active(self.app.clip_triggering_mode):
            try:
                encoder_num = [
                    push2_python.constants.ENCODER_TRACK1_ENCODER,
                    push2_python.constants.ENCODER_TRACK2_ENCODER,
                    push2_python.constants.ENCODER_TRACK3_ENCODER,
                    push2_python.constants.ENCODER_TRACK4_ENCODER,
                    push2_python.constants.ENCODER_TRACK5_ENCODER,
                    push2_python.constants.ENCODER_TRACK6_ENCODER,
                    push2_python.constants.ENCODER_TRACK7_ENCODER,
                    push2_python.constants.ENCODER_TRACK8_ENCODER,
                ].index(encoder_name)
                
                # Get the CC number mapped to this encoder
                if encoder_num < len(self.active_midi_control_ccs):
                    cc_control = self.active_midi_control_ccs[encoder_num]
                    cc_number = cc_control.cc_number
                    
                    # Get current value and update it
                    hardware_device = self.state.get_output_hardware_device_by_name(
                        self.get_current_track_device_short_name_helper())
                    if hardware_device is not None:
                        current_value = hardware_device.get_current_midi_cc_parameter_value(cc_number)
                        # Update value based on increment (clamp to 0-127)
                        new_value = max(0, min(127, current_value + increment))
                        
                        # Send control change to hardware device
                        try:
                            hardware_device.set_midi_cc_parameter_value(cc_number, new_value)
                        except AttributeError:
                            # Fallback for devices that don't have this method
                            print(f"DEBUG: Hardware device doesn't support set_midi_cc_parameter_value, CC {cc_number} = {new_value}")
                        except Exception as e:
                            print(f"DEBUG: Error setting MIDI CC {cc_number}: {e}")
                        
                return True  # Always return True because encoder should not be used in any other mode if this is first active
            except ValueError:
                pass  # Encoder not in list
        
