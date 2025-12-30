from nicegui import ui
from pages.theme import frame
from functions.config_functions import load_all_config, update_config, get_config

SETTING_BOX_COLOUR = '0F132D'

def content():
    def whitelist_toggle(value):
        update_config('whitelist_toggle', value)
        
    def country_code_update(value):
        # check length between 2 and 5 (including +)
        if len(value) < 1 or len(value) > 6: 
            ui.notify('Country code length should be between 1 and 4 digits after +.', color='red')
            return
        # Check code starts with + and followed by digits (with optional - to handle some countries)
        if not value.startswith('+') or not value[1:].replace('-', '').isdigit():
            ui.notify('Invalid country code. It should start with + followed by digits.', color='red')
            return
        
        nonlocal config_data # Use nonlocal to modify the outer variable
        config_data = update_config('country_code', value)
        ui.notify('Country code updated.', color='green')
        country_code_button.disable()
    
    def modem_interface_update(value):
        nonlocal config_data # Use nonlocal to modify the outer variable
        config_data = update_config('modem_interface', value)
        modem_interface_button.disable()
    
    def country_code_change_check(value):
        if value != config_data['country_code']:
            country_code_button.enable()
        else:
            country_code_button.disable()
    def modem_interface_change_check(value):
        if value != config_data['modem_interface']:
            modem_interface_button.enable()
        else:
            modem_interface_button.disable()
            
    config_data = load_all_config()
    
    with frame('Settings'):
        ui.label('Settings Page').classes('text-2xl mt-2')
                
        with ui.row().classes('mt-4 w-full h-full gap-4'):
            with ui.card().classes('w-1/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('SMS Settings')
                ui.checkbox('Whitelist', value=config_data['whitelist_toggle'], on_change=lambda e: whitelist_toggle(e.value))
                with ui.row():
                    country_code_input = ui.input('Country Code', value=config_data['country_code'], on_change=lambda e: country_code_change_check(e.value)).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    country_code_button = ui.button('Set code', on_click=lambda: country_code_update(country_code_input.value)).classes('mt-4')
                    country_code_button.disable()
                with ui.row():
                    modem_interface_input = ui.input('Modem Interface', value=config_data['modem_interface'], on_change=lambda e: modem_interface_change_check(e.value)).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    modem_interface_button = ui.button('Set interface', on_click=lambda: modem_interface_update(modem_interface_input.value)).classes('mt-4')
                    modem_interface_button.disable()
            
            with ui.card().classes('w-1/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('AI Settings')
                