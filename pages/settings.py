from nicegui import ui
from pages.theme import frame
from functions.config_functions import load_all_config, update_config, get_config

SETTING_BOX_COLOUR = '0F132D'

def content():
    # Check country code is changed
    def country_code_change_check():
        if country_code_input.value != config_data['country_code']:
            country_code_button.enable()
        else:
            country_code_button.disable()
            
    # Check modem interface change
    def modem_interface_change_check():
        if modem_interface_input.value != config_data['modem_interface']:
            modem_interface_button.enable()
        else:
            modem_interface_button.disable()
    
    # Check system location change
    def sys_location_change_check():
        # Convert inputs to location data dictionary
        location_data = {
            'city': sys_city_input.value,
            'region': sys_region_input.value,
            'country': sys_country_input.value
        }
        
        # Compare with stored config location dictionary
        if location_data != config_data.get('location', {}):
            sys_location_button.enable()
        else:
            sys_location_button.disable()
       
    # Check prompt instructions change
    def instructions_change_check():
        if llm_prompt_input.value != config_data.get('prompt_instructions', ''):
            llm_prompt_button.enable()
        else:
            llm_prompt_button.disable()
    
    # Check llm input changes
    #TODO: implement global llm change detections
    
    # Update whitelist toggle
    def whitelist_toggle(value):        
        update_config('whitelist_toggle', value)
            
    # Update country code
    def country_code_update():    
        new_country_code = country_code_input.value.strip()
            
        # check length between 2 and 5 (including +)
        if len(new_country_code) < 1 or len(new_country_code) > 6: 
            ui.notify('Country code length should be between 1 and 4 digits after +.', color='red')
            return
        # Check code starts with + and followed by digits (with optional - to handle some countries)
        if not new_country_code.startswith('+') or not new_country_code[1:].replace('-', '').isdigit():
            ui.notify('Invalid country code. It should start with + followed by digits.', color='red')
            return
        
        nonlocal config_data # Use nonlocal to modify the outer variable
        config_data = update_config('country_code', new_country_code)
        ui.notify('Country code updated.', color='green')
        country_code_button.disable()
    
    # Update interface for modem
    def modem_interface_update():
        nonlocal config_data # Use nonlocal to modify the outer variable
        
        new_interface = modem_interface_input.value.strip()
        
        config_data = update_config('modem_interface', new_interface)
        modem_interface_button.disable()
    
    # Update system location
    def sys_location_update():
        location_data = {
            'city': sys_city_input.value,
            'region': sys_region_input.value,
            'country': sys_country_input.value
        }
        nonlocal config_data # Use nonlocal to modify the outer variable
        config_data = update_config('location', location_data)
        ui.notify('System location updated.', color='green')
        sys_location_button.disable()   
    
    # Update prompt instructions
    def instructions_update():
        new_instructions = llm_prompt_input.value.strip()
        
        nonlocal config_data # Use nonlocal to modify the outer variable
        config_data = update_config('prompt_instructions', new_instructions)
        
        ui.notify('LLM prompt instructions updated.', color='green')
        llm_prompt_button.disable()
        
    
    
    config_data = load_all_config()
    
    with frame('Settings'):
        ui.label('Settings Page').classes('text-2xl mt-2')
        
        # System Settings
        with ui.card().classes('min-w-[500px] w-2/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
            ui.label('System Settings').classes('text-lg mb-2 underline')
            
            # Extract location data for better readability
            location_data = config_data.get('location', {})
            
            # System Location   
            with ui.row():
                sys_city_input = ui.input('System Location (city)', value=location_data.get('city', ''), on_change=lambda e: sys_location_change_check()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
                sys_region_input = ui.input('System Location (region)', value=location_data.get('region', ''), on_change=lambda e: sys_location_change_check()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
                sys_country_input = ui.input('System Location (country)', value=location_data.get('country', ''), on_change=lambda e: sys_location_change_check()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
                sys_location_button = ui.button('Set Location', on_click=lambda: sys_location_update()).classes('mt-4')
                sys_location_button.disable()
                       
        with ui.row().classes('mt-4 w-full no-wrap items-start'):
            # SMS Settings
            with ui.card().classes('min-w-[400px] w-1/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('SMS Settings').classes('text-lg mb-2 underline')
                
                # Whitelist Toggle
                ui.checkbox('Whitelist', value=config_data.get('whitelist_toggle'), on_change=lambda e: whitelist_toggle(e.value)).props('dark color="grey"')
                # Country Code and Modem Interface
                with ui.row():
                    country_code_input = ui.input('Country Code', value=config_data.get('country_code',''), on_change=lambda e: country_code_change_check()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    country_code_button = ui.button('Set code', on_click=lambda: country_code_update()).classes('mt-4')
                    country_code_button.disable()
                # Modem Interface  
                with ui.row():
                    modem_interface_input = ui.input('Modem Interface', value=config_data.get('modem_interface', ''), on_change=lambda e: modem_interface_change_check()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    modem_interface_button = ui.button('Set interface', on_click=lambda: modem_interface_update()).classes('mt-4')
                    modem_interface_button.disable()

            # AI Settings 
            # TODO: add api keys selection
            with ui.card().classes('min-w-[550px] w-1/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('AI Settings').classes('text-lg mb-2 underline')
                
                
                llm_config = config_data['llm_configs']
                gemini_config = llm_config['gemini_config']
                openai_config = llm_config['chatgpt_config']
                deepseek_config = llm_config['deepseek_config']
                claude_config = llm_config['claude_config']
                mistral_config = llm_config['mistral_config']
                
                gemini_options = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-3-pro']
                
                # LLM Prompt
                with ui.row():
                    llm_prompt_input = ui.textarea('LLM Instructions', value=config_data.get('prompt_instructions', ''), on_change=lambda e: instructions_change_check()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-64 h-48 mt-4')
                    llm_prompt_button = ui.button('Set default LLM prompt', on_click=lambda: instructions_update()).classes('mt-4')
                
                # Gemini 
                with ui.row():
                    gemini_api_key_input = ui.input('Gemini API Key', value=gemini_config.get('api_key', ''), on_change=lambda e: gemini_api_key_change_check()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_model_select_input = ui.select(gemini_options, label='Gemini Model', value=gemini_config.get('model', ''), on_change=lambda e: gemini_model_change_check()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_api_key_button = ui.button('Set API Key', on_click=lambda: gemini_api_key_update()).classes('mt-4')
                    gemini_api_key_button.disable()