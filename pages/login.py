from nicegui import ui, app
import os, hmac, hashlib

colour_bg = '0d1331'  # Very dark blue

def check_password(inputed_password):
    inputed_password = inputed_password.encode('utf-8')
    
    hashed_input = hmac.new(inputed_password, b"thisIsASalt", hashlib.sha512).digest()
    
    # If setup has been completed before, read stored password
    if os.path.exists("data/config.txt"):
        with open("data/config.txt", "r") as f:
            stored_password = f.readline().strip()
    
    # Check if inputed password matches stored password
    return hashed_input.hex() == stored_password # Return boolean


def content():
    ui.query('body').style(f'background-color: #{colour_bg}')

    def check_input(inputed_password):
        if check_password(inputed_password):
            app.storage.user['authenticated'] = True # Set authenticated flag
            ui.navigate.to('/home')
        else:
            return ui.notify('Incorrect password', color='red')
       

    with ui.column().classes('absolute-center items-center'):
        ui.label('BluChat login').classes('text-2xl mt-2 text-white')
        
        input_box = ui.input(label='Enter password', password=True).props('input-style="color: white" label-color="white"').classes('w-full max-w-sm mt-4')
        
        ui.button('Login', on_click=lambda: check_input(input_box.value)).classes('mt-4 text-white')