from nicegui import ui, app
import os, hmac, hashlib, time

colour_bg = '0d1331'  # Very dark blue

def content():
    ui.query('body').style(f'background-color: #{colour_bg}')

    def check_input(inputed_password):
        inputed_password = inputed_password.encode('utf-8') # Encode to bytes
        # use browser key as a salt
        with open('data/browser_key.txt', 'r') as f:
            browser_key = f.read().strip().encode('utf-8')
        
        # Hash the inputed password
        hashed_input = hmac.new(inputed_password, browser_key, hashlib.sha512).digest() 
        
        # Create debug log for setup process
        setup_log = ui.log().classes('mt-4 max-h-40 w-full max-w-sm')
        setup_log.push(f'Hashed input: {hashed_input.hex()}')
        
        # First time setup: create data directory and files if they don't exist
        setup_log.push('Setting up data directory and files...')
        os.makedirs("data", exist_ok=True)
        open("data/config.txt", "a").close()
        open("data/authorised_numbers.txt", "a").close()   
        
        # save the hashed password during setup
        setup_log.push('Storing hashed password...')
        with open("data/config.txt", "a") as f:
            f.write(hashed_input.hex())
            
            app.storage.tab['authenticated'] = True # Set authenticated flag
            app.storage.tab['last_active'] = time.time() # Set last active time
            app.storage.tab['password'] = inputed_password # Store password in session storage
            ui.navigate.to('/home')

    with ui.column().classes('absolute-center items-center'):
        ui.label('Welcome to BluChat Setup').classes('text-2xl mt-2 text-white')
        input_box = ui.input(label='Set a password', password=True).props('input-style="color: white" label-color="white"').classes('w-full max-w-sm mt-4')
        
        ui.button('Setup', on_click=lambda: check_input(input_box.value)).classes('mt-4 text-white')