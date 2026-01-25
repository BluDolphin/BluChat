from nicegui import ui, app
import time, json, requests
from functions.encryption_functions import hash_password
from functions.config_functions import initialise_config

colour_bg = '0d1331'  # Very dark blue

def content():
    ui.query('body').style(f'background-color: #{colour_bg}')

    def check_input(inputed_password):
        # Validate password input
        if inputed_password == '' or inputed_password is None:
            ui.notify('Password cannot be empty', color='red')
            return
        
        inputed_password = inputed_password.encode('utf-8') # Encode to bytes
        hashed_input = hash_password(inputed_password) # Hash the inputed password

        # Create debug log for setup process
        setup_log = ui.log().classes('mt-4 max-h-40 w-full max-w-sm')
        setup_log.push(f'Hashed input: {hashed_input}')
        
        # Obtain system location via ipinfo.io
        try:
            # If auto location detection is enabled
            if auto_location_checkbox.value == False:
                raise Exception('Auto location disabled by user.')
            
            setup_log.push('Auto location detection enabled.')
            setup_log.push('Obtaining system location... from ipinfo.io')
            response = requests.get('https://ipinfo.io/json')
            data = response.json() # Convert response to JSON
            
            # Extract city, region, country
            location_data =  {
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country')
            }
        except Exception as e: # On failure or disabled
            setup_log.push(f'Error obtaining system location: {str(e)}\n Continuing setup without location data.')
            # Set no location
            location_data = {
                'city': '',
                'region': '',
                'country': ''
                }
            
        setup_log.push(f'Location data: {location_data}')   
        # First time setup: create data directory and files if they don't exist
        setup_log.push('Setting up data directory and files...')
        
        
        initialise_config(location_data) # Initialise config without location data
        open('data/authorised_numbers.json', 'a').close() # Create empty authorised numbers file if not exist 
        open('data/group_list.json', 'a').close() # Create empty group list file if not exist
        
        # save the hashed password during setup
        setup_log.push('Storing hashed password...')
        
        # Write hashed password 2nd line of crypt_data.json
        with open('data/crypt_data.json', 'r') as f:
            stored_data = json.load(f)
            
        stored_data['password'] = hashed_input.hex()
        
        with open('data/crypt_data.json', 'w') as f:
            json.dump(stored_data, f, indent=4)
            
        app.storage.tab['authenticated'] = True # Set authenticated flag
        app.storage.tab['last_active'] = time.time() # Set last active time
        app.storage.tab['password'] = inputed_password # Store password in session storage
        ui.navigate.to('/home')

    with ui.column().classes('absolute-center items-center'):
        ui.label('Welcome to BluChat Setup').classes('text-2xl mt-2 text-white')
        input_box = ui.input(label='Set a password', password=True).props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-full max-w-sm mt-4')
        auto_location_checkbox = ui.checkbox('Automatically detect location (via ipinfo.io)', value=True).classes('mt-4 text-white').props('color="dark-gray"')    
        ui.button('Setup', on_click=lambda: check_input(input_box.value)).classes('mt-4 text-white')