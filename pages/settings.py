from nicegui import app, ui
import copy, asyncio
from pages.theme import frame
from functions.config_functions import load_all_config, update_config
from functions.encryption_functions import decrypt_data
from functions.llm_functions import check_llm_config, update_llm_values, update_instructions, update_active_llm
from pages.theme import check_timeout

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
        if str(llm_prompt_input.value).strip() != stored_instructions:
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
        check_timeout(True)  # Reset timeout timer
        
        update_config('whitelist_toggle', value) # Update config
        
        ui.notify('Whitelist setting updated.', color='green')
            
    # Update country code
    def country_code_update():
        check_timeout(True)  # Reset timeout timer
        
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
        check_timeout(True)  # Reset timeout timer
        
        # Pass config_data as its used to check for updates to input fields
        nonlocal config_data # Use nonlocal to access config_data
        new_interface = modem_interface_input.value.strip() # Get new interface value
        config_data = update_config('modem_interface', new_interface) # Update config
        
        ui.notify('Modem interface updated.', color='green')
        modem_interface_button.disable()
    
    # Update system location
    def sys_location_update():
        check_timeout(True)  # Reset timeout timer
        
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
        check_timeout(True)  # Reset timeout timer
        
        nonlocal config_data # Use nonlocal to access config_data
        
        # Update instructions in config
        config_data = update_instructions(llm_prompt_input.value.strip(), app.storage.tab.get('password'))
             
        ui.notify('LLM prompt instructions updated.', color='green')
        llm_prompt_button.disable()
    
    # Update default for the input changes 
    # This includes when it automatically is updated after validating LLM configs
    def default_llm_update():
        check_timeout(True)  # Reset timeout timer
        
        nonlocal valid_llm_options # Use nonlocal to access valid_llm_options
        
        selected_llm = llm_default_dropdown.value # Get selected llm from dropdown
        
        # Error handling if values are removed by changed usability
        if selected_llm is None or selected_llm == 'No Usable LLM Configured': # If value is None
            update_active_llm('') # Save empty active llm
            llm_default_dropdown.value = 'No Usable LLM Configured' # Reset dropdown value
            valid_llm_options.insert(0, 'No Usable LLM Configured') if 'No Usable LLM Configured' not in valid_llm_options else None # Add to valid options list uf not present
        else:
            update_active_llm(selected_llm.lower()) # Update active llm in config
        
        ui.notify('Default LLM updated.', color='green')
        
    # Validate all LLM configurations
    async def validate_all():
        check_timeout(True)  # Reset timeout timer
        
        nonlocal valid_llm_options # Use nonlocal to access valid_llm_options

        ui.notify('Validating all LLM configurations. Please Wait...', color='orange')
        validate_all_button.disable()
        
        
        # Loop through all LLM's and validate configs
        for llm in ['gemini', 'mistral', 'chatgpt', 'deepseek', 'claude']:
            try:
                response = await asyncio.to_thread(check_llm_config, llm, app.storage.tab.get('password'))
                
                # If error, notify user
                if response != 0: 
                    raise Exception(f"{response[0]}:{response[1]}")
                
                # If no error, notify success
                dropdown_changed(llm, True) # Call dropdown changed to update valid options
                ui.notify(f'validated {llm} configuration.', color='green') # Notify success
                
            except Exception as e:
                dropdown_changed(llm, False) # Call dropdown changed to update valid options
                ui.notify(f'Error validating {llm} configuration: {str(e)}', color='red')
                
                    
        ui.notify('LLM configuration validation complete.', color='green')
        validate_all_button.enable()
    
    
    # Update LLM configuration (singular button)
    # Using async to avoid blocking ui during validation
    async def llm_config_update(llm_name, new_api_key, new_llm_model, button):
        check_timeout(True)  # Reset timeout timer
        
        # Pass config_data as its used to check for updates to input fields
        nonlocal stored_llm_config # Use nonlocal to access stored_llm_config
        nonlocal valid_llm_options

        ui.notify(f'Validating {llm_name} configuration. Please Wait...', color='orange')
        button.disable() # Disable button to prevent multiple clicks
        
        # check validity of entered api config
        # Use await to pause function while thread runs
        response = await asyncio.to_thread(check_llm_config, llm_name, app.storage.tab.get('password'), (new_api_key, new_llm_model))
        if response != 0:
            ui.notify(f'Error validating LLM configuration: {response[0]}:{response[1]}', color='red')
            button.enable() # Re-enable button
            return
        
        update_llm_values(llm_name, new_api_key, new_llm_model, app.storage.tab.get('password'))

        # Save unencrypted key for displaying to user
        stored_llm_config[f"{llm_name}_config"]['api_key'] = new_api_key 
        stored_llm_config[f"{llm_name}_config"]['model'] = new_llm_model   
        
        dropdown_changed(llm_name, True) # Call dropdown changed to update valid options
        
        ui.notify('LLM configuration updated.', color='green')
        button.props('color=green') # Change button to green to indicate valid config
        button.disable()
    
    
    # Handle dropdown changes to update valid options
    # Also changes button colours based on usability
    # Used by the validate all and individual llm config update functions
    def dropdown_changed(llm, add_or_remove):
        nonlocal valid_llm_options # Use nonlocal to access valid_llm_options
        nonlocal llm_button_colours # Use nonlocal to access llm_default_dropdown
        
        # Dictionary to map LLM names to their save buttons
        llm_buttons = {
            'gemini': gemini_save_button,
            'mistral': mistral_save_button,
            'chatgpt': chatgpt_save_button,
            'deepseek': deepseek_save_button,
            'claude': claude_save_button
        }
        
        if add_or_remove == True:
            # Add to valid options if not already present
            if llm.capitalize() not in valid_llm_options:
                valid_llm_options.append(llm.capitalize()) # Add to valid options list
                llm_default_dropdown.options = valid_llm_options # Update dropdown options
                llm_default_dropdown.update() # Refresh dropdown
                
                llm_buttons[llm].props('color=green') # Change button to green to indicate valid config
        
        if add_or_remove == False:
            # Remove from valid options if present
            if llm.capitalize() in valid_llm_options:
                valid_llm_options.remove(llm.capitalize()) # Remove from valid options list
                llm_default_dropdown.options = valid_llm_options # Update dropdown options
                llm_default_dropdown.update() # Refresh dropdown
                
                llm_buttons[llm].props('color=red') # Change button to red to indicate invalid config
            
    
    
    config_data = load_all_config() # Load current config data
    # Get stored llm_configs which will be decrypted for displaying to user
    stored_llm_config = copy.deepcopy(config_data['llm_configs']) # Deep copy to avoid modifying original data 
    # Decrypt stored prompt instructions for display
    stored_instructions = decrypt_data(config_data.get('prompt_instructions', ''), app.storage.tab.get('password'))

    
    # Determine button colours for LLM's
    llm_button_colours = {
        'gemini': '',
        'mistral': '',
        'chatgpt': '',
        'deepseek': '',
        'claude': ''}
    # List of valid llm options for dropdown
    valid_llm_options = [] 

    
    # Decrypt stored API keys for display
    # Store decrypted keys in the copied dictionary only
    for llm_config in stored_llm_config:
        # Decrypt API keys for display
        encrypted_api_key = stored_llm_config[llm_config]['api_key'] # Get encrypted api key
        decrypted_key = decrypt_data(encrypted_api_key, app.storage.tab.get('password')) # Decrypt api key
        stored_llm_config[llm_config]['api_key'] = decrypted_key # Store decrypted key back in copied dictionary
        
        # Extract button colours for each LLM
        llm_name = llm_config.replace('_config', '') # Get llm name without _config
        if stored_llm_config[llm_config].get('usable', False) == True: # If usable, set button to green and add as a valid options
            llm_button_colours[llm_name] = 'green'
            valid_llm_options.append(llm_name.capitalize()) # Add to valid options list
        else: # Otherwise set to red
            llm_button_colours[llm_name] = 'red'
        
    # Get Active LLM
    # If active_llm is not in valid options, use it
    active_llm_value = config_data.get('active_llm')
    if active_llm_value == '' or active_llm_value == None or active_llm_value.capitalize() not in valid_llm_options:
        # Add "No Default Selected" as an option and select
        active_llm_value = 'No Usable LLM Configured'
        valid_llm_options.insert(0, 'No Usable LLM Configured')

    
    # Main content within the themed frame    
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
                
                # LLM Prompt Instructions 
                with ui.row().classes('w-full gap-10'):
                    llm_prompt_input = ui.textarea('LLM Instructions', value=stored_instructions, on_change=lambda e: check_for_changes()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-64 h-48 mt-4')
                    llm_prompt_button = ui.button('Set LLM Instructions', on_click=lambda: instructions_update()).classes('mt-2')
                    llm_prompt_button.disable()
                            
                # Validate LLM configs and default llm 
                with ui.row().classes('w-full gap-15'):
                    validate_all_button = ui.button('Manually Validate All Configs', on_click=lambda: validate_all()).classes('mt-4')
                    llm_default_dropdown = ui.select(label='Default LLM for chats:', value=active_llm_value, options=valid_llm_options, on_change=lambda e: default_llm_update()).props('dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-52')

                        
                # LLM Configurations
                # Free tiers
                with ui.row().classes('w-full mt-4'): # Gemini
                    gemini_api_input = ui.input('Gemini API Key', value=stored_llm_config['gemini_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_model_input = ui.input(label='Gemini Model', value=stored_llm_config['gemini_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    gemini_save_button = ui.button('Save Settings', color=llm_button_colours.get('gemini', 'red'), on_click=lambda: llm_config_update('gemini', gemini_api_input.value.strip(), gemini_model_input.value, gemini_save_button)).classes('mt-4')
                    gemini_save_button.disable()
                with ui.row(): # Mistral
                    mistral_api_input = ui.input('Mistral API Key', value=stored_llm_config['mistral_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    mistral_model_input = ui.input(label='Mistral Model', value=stored_llm_config['mistral_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    mistral_save_button = ui.button('Save Settings', color=llm_button_colours.get('mistral', 'red'), on_click=lambda: llm_config_update('mistral', mistral_api_input.value.strip(), mistral_model_input.value, mistral_save_button)).classes('mt-4')
                    mistral_save_button.disable()
                    
                # Paid tiers
                with ui.row(): # ChatGPT
                    chatgpt_api_input = ui.input('ChatGPT API Key', value=stored_llm_config['chatgpt_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    chatgpt_model_input = ui.input(label='ChatGPT Model', value=stored_llm_config['chatgpt_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    chatgpt_save_button = ui.button('Save Settings', color=llm_button_colours.get('chatgpt', 'red'), on_click=lambda: llm_config_update('chatgpt', chatgpt_api_input.value.strip(), chatgpt_model_input.value, chatgpt_save_button)).classes('mt-4')
                    chatgpt_save_button.disable()
                with ui.row(): # DeepSeek
                    deepseek_api_input = ui.input('DeepSeek API Key', value=stored_llm_config['deepseek_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    deepseek_model_input = ui.input(label='DeepSeek Model', value=stored_llm_config['deepseek_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    deepseek_save_button = ui.button('Save Settings', color=llm_button_colours.get('deepseek', 'red'), on_click=lambda: llm_config_update('deepseek', deepseek_api_input.value.strip(), deepseek_model_input.value, deepseek_save_button)).classes('mt-4')
                    deepseek_save_button.disable()
                with ui.row(): # Claude
                    claude_api_input = ui.input('Claude API Key', value=stored_llm_config['claude_config'].get('api_key', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    claude_model_input = ui.input(label='Claude Model', value=stored_llm_config['claude_config'].get('model', ''), on_change=lambda e: check_for_changes()).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('mt-4 mr-4')
                    claude_save_button = ui.button('Save Settings', color=llm_button_colours.get('claude', 'red'), on_click=lambda: llm_config_update('claude', claude_api_input.value.strip(), claude_model_input.value, claude_save_button)).classes('mt-4')
                    claude_save_button.disable()

