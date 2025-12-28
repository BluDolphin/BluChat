from nicegui import app, ui
import copy
from pages.theme import frame
from functions.config_functions import load_all_config, update_config
from functions.encryption_functions import encrypt_data, decrypt_data

SETTING_BOX_COLOUR = '0F132D'

def content():
    # Global function to check for changes in inputs and enable/disable save buttons
    def check_for_changes():
        # --Check country code is changed--
        if country_code_input.value != config_data.get('country_code', ''):
            country_code_button.enable()
        else:
            country_code_button.disable()
            
        # --Check modem interface change--
        if modem_interface_input.value != config_data.get('modem_interface', ''):
            modem_interface_button.enable()
        else:
            modem_interface_button.disable()
    
        # --Check system location change--
        # Convert inputs to location data dictionary
        location_data = {
            'city': sys_city_input.value,
            'region': sys_region_input.value,
            'country': sys_country_input.value
        }
        
        # Compare with stored config location dictionary
        if location_data != config_data.get('location'):
            sys_location_button.enable()
        else:
            sys_location_button.disable()
       
        # --Check prompt instructions change--
        # Decrypt stored instructions for comparison
        stored_instructions = str(decrypt_data(config_data.get('prompt_instructions', ''), app.storage.tab.get('password')))
        if llm_prompt_input.value.strip() != stored_instructions:
            llm_prompt_button.enable()
        else:
            llm_prompt_button.disable()


        # --LLM config checks--
        # Get stored LLM configs for comparison
        gemini_config = stored_llm_config.get('gemini_config')
        mistral_config = stored_llm_config.get('mistral_config')
        openai_config = stored_llm_config.get('chatgpt_config')
        deepseek_config = stored_llm_config.get('deepseek_config')
        claude_config = stored_llm_config.get('claude_config')
        
        # --Check Gemini settings change--
        # If api key or model changed, enable save button
        if gemini_api_input.value != gemini_config.get('api_key', '') or \
            gemini_model_input.value != gemini_config.get('model', ''):
            gemini_save_button.enable()
        else:
            gemini_save_button.disable()
        # --Check Mistral settings change--
        # If api key or model changed, enable save button
        if mistral_api_input.value != mistral_config.get('api_key', '') or \
            mistral_model_input.value != mistral_config.get('model', ''):
            mistral_save_button.enable()
        else:
            mistral_save_button.disable()
        # --Check ChatGPT settings change--
        # If api key or model changed, enable save button
        if chatgpt_api_input.value != openai_config.get('api_key', '') or \
            chatgpt_model_input.value != openai_config.get('model', ''):
            chatgpt_save_button.enable()
        else:
            chatgpt_save_button.disable()
        # --Check DeepSeek settings change--
        # If api key or model changed, enable save button
        if deepseek_api_input.value != deepseek_config.get('api_key', '') or \
            deepseek_model_input.value != deepseek_config.get('model', ''):
            deepseek_save_button.enable()
        else:
            deepseek_save_button.disable()
        # --Check Claude settings change--
        # If api key or model changed, enable save button
        if claude_api_input.value != claude_config.get('api_key', '') or \
            claude_model_input.value != claude_config.get('model', ''):
            claude_save_button.enable()
        else:
            claude_save_button.disable()

    
    # --- Configuration update functions ---
    # Update whitelist toggle
    def whitelist_toggle(value):        
        update_config('whitelist_toggle', value)
        
        ui.notify('Whitelist setting updated.', color='green')
            
    # Update country code
    def country_code_update():
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data    
        new_country_code = country_code_input.value.strip()
            
        # check length between 2 and 5 (including +)
        if len(new_country_code) < 1 or len(new_country_code) > 6: 
            ui.notify('Country code length should be between 1 and 4 digits after +.', color='red')
            return
        # Check code starts with + and followed by digits (with optional - to handle some countries)
        if not new_country_code.startswith('+') or not new_country_code[1:].replace('-', '').isdigit():
            ui.notify('Invalid country code. It should start with + followed by digits.', color='red')
            return
        
        config_data = update_config('country_code', new_country_code) # Update config
        
        ui.notify('Country code updated.', color='green')
        country_code_button.disable()
    
    # Update interface for modem
    def modem_interface_update():
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data
        new_interface = modem_interface_input.value.strip() # Get new interface value
        config_data = update_config('modem_interface', new_interface) # Update config
        
        ui.notify('Modem interface updated.', color='green')
        modem_interface_button.disable()
    
    # Update system location
    def sys_location_update():
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data
        # Convert inputs to location data dictionary
        location_data = {
            'city': sys_city_input.value,
            'region': sys_region_input.value,
            'country': sys_country_input.value
        }
        config_data = update_config('location', location_data)
        
        ui.notify('System location updated.', color='green')
        sys_location_button.disable()   
    
    # Update prompt instructions
    def instructions_update():
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data
        new_instructions = encrypt_data(llm_prompt_input.value.strip(), app.storage.tab.get('password'))
        config_data = update_config('prompt_instructions', new_instructions)
        
        ui.notify('LLM prompt instructions updated.', color='green')
        llm_prompt_button.disable()
    
    # Update LLM configuration
    def llm_config_update(config_target, new_api_key, new_llm_model, button):
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data
        nonlocal stored_llm_config # Use nonlocal to access stored_llm_config

        # check validity of api
        pass # Placeholder for actual API key validation logic will use a function specified by config_target to identify service
        
        
        # Save unencrypted key for displaying to user
        stored_llm_config[config_target]['api_key'] = new_api_key 
        stored_llm_config[config_target]['model'] = new_llm_model
        
        # Encrypt and store the new configuration
        new_llm_configs = config_data['llm_configs'] # Get existing llm_configs (encrypted) and save to a variable
        targets_config = new_llm_configs[config_target] # Get existing target LLM config
        encrypted_api_key = encrypt_data(new_api_key, app.storage.tab.get('password')) # Encrypt API key before storing
        
        # Update with new values
        targets_config['api_key'] = encrypted_api_key
        targets_config['model'] = new_llm_model 
        
        new_llm_configs[config_target] = targets_config # Save changes back to llm_configs
        config_data = update_config('llm_configs', new_llm_configs) # Save updated llm_configs back to main config
        
        ui.notify('LLM configuration updated.', color='green')
        button.disable()
    
    
    config_data = load_all_config() # Load current config data
    stored_llm_config = copy.deepcopy(config_data['llm_configs']) # Deep copy to avoid modifying original data
    
    # Decrypt stored API keys for display
    # Store decrypted keys in the copied dictionary only
    for llm in stored_llm_config:
        # Decrypt API keys for display
        encrypted_key = stored_llm_config[llm]['api_key']
        if encrypted_key:
            decrypted_key = decrypt_data(encrypted_key, app.storage.tab.get('password'))
            stored_llm_config[llm]['api_key'] = decrypted_key
        else:
            stored_llm_config[llm]['api_key'] = ''
       
    
    with frame('Settings'):
        ui.label('Settings Page').classes('text-2xl mt-2')
        
        # System Settings
        with ui.card().classes('min-w-[500px] w-2/3 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
            ui.label('System Settings').classes('text-lg mb-2 underline')
                
            # Extract location data for better readability
            location_data = config_data.get('location', {})
            
            # System Location   
            with ui.row():
                sys_city_input = ui.input('System Location (city)', value=location_data.get('city', ''), on_change=lambda e: check_for_changes()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
                sys_region_input = ui.input('System Location (region)', value=location_data.get('region', ''), on_change=lambda e: check_for_changes()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
                sys_country_input = ui.input('System Location (country)', value=location_data.get('country', ''), on_change=lambda e: check_for_changes()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52 mt-4')
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
                    country_code_input = ui.input('Country Code', value=config_data.get('country_code',''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    country_code_button = ui.button('Set code', on_click=lambda: country_code_update()).classes('mt-4')
                    country_code_button.disable()
                # Modem Interface  
                with ui.row():
                    modem_interface_input = ui.input('Modem Interface', value=config_data.get('modem_interface', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    modem_interface_button = ui.button('Set interface', on_click=lambda: modem_interface_update()).classes('mt-4')
                    modem_interface_button.disable()

            # AI Settings 
            with ui.card().classes('min-w-[600px] w-3/7 h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('AI Settings').classes('text-lg mb-2 underline')
                
                # LLM Prompt
                with ui.row():
                    llm_prompt_input = ui.textarea('LLM Instructions', value=decrypt_data(config_data.get('prompt_instructions', ''), app.storage.tab.get('password')), on_change=lambda e: check_for_changes()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-64 h-48 mt-4')
                    llm_prompt_button = ui.button('Set default LLM prompt', on_click=lambda: instructions_update()).classes('mt-4')
                    llm_prompt_button.disable()
                    
                
                # LLM Configurations
                # Free tiers
                with ui.row(): # Gemini
                    gemini_api_input = ui.input('Gemini API Key', value=stored_llm_config['gemini_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_model_input = ui.input(label='Gemini Model', value=stored_llm_config['gemini_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_save_button = ui.button('Save Settings', on_click=lambda: llm_config_update('gemini_config', gemini_api_input.value.strip(), gemini_model_input.value, gemini_save_button)).classes('mt-4')
                    gemini_save_button.disable()
                with ui.row(): # Mistral
                    mistral_api_input = ui.input('Mistral API Key', value=stored_llm_config['mistral_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    mistral_model_input = ui.input(label='Mistral Model', value=stored_llm_config['mistral_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    mistral_save_button = ui.button('Save Settings', on_click=lambda: llm_config_update('mistral_config', mistral_api_input.value.strip(), mistral_model_input.value, mistral_save_button)).classes('mt-4')
                    mistral_save_button.disable()
                    
                # Paid tiers
                with ui.row(): # ChatGPT
                    chatgpt_api_input = ui.input('ChatGPT API Key', value=stored_llm_config['chatgpt_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    chatgpt_model_input = ui.input(label='ChatGPT Model', value=stored_llm_config['chatgpt_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    chatgpt_save_button = ui.button('Save Settings', on_click=lambda: llm_config_update('chatgpt_config', chatgpt_api_input.value.strip(), chatgpt_model_input.value, chatgpt_save_button)).classes('mt-4')
                    chatgpt_save_button.disable()
                with ui.row(): # DeepSeek
                    deepseek_api_input = ui.input('DeepSeek API Key', value=stored_llm_config['deepseek_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    deepseek_model_input = ui.input(label='DeepSeek Model', value=stored_llm_config['deepseek_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    deepseek_save_button = ui.button('Save Settings', on_click=lambda: llm_config_update('deepseek_config', deepseek_api_input.value.strip(), deepseek_model_input.value, deepseek_save_button)).classes('mt-4')
                    deepseek_save_button.disable()
                with ui.row(): # Claude
                    claude_api_input = ui.input('Claude API Key', value=stored_llm_config['claude_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    claude_model_input = ui.input(label='Claude Model', value=stored_llm_config['claude_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    claude_save_button = ui.button('Save Settings', on_click=lambda: llm_config_update('claude_config', claude_api_input.value.strip(), claude_model_input.value, claude_save_button)).classes('mt-4')
                    claude_save_button.disable()
