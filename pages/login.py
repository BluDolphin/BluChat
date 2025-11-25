from nicegui import ui, app
from functions.check_password import check_password
import time

colour_bg = '0d1331'  # Very dark blue

def content():
    ui.query('body').style(f'background-color: #{colour_bg}')
    
    def check_input(inputed_password):
        if check_password(inputed_password):
            app.storage.tab['authenticated'] = True # Set authenticated flag
            app.storage.tab['last_active'] = time.time() # Set last active time
            ui.navigate.to('/home')
        else:
            return ui.notify('Incorrect password', color='red')
       

    with ui.column().classes('absolute-center items-center'):
        ui.label('BluChat login').classes('text-2xl mt-2 text-white')
        
        input_box = ui.input(label='Enter password', password=True).props('input-style="color: white" label-color="white"').classes('w-full max-w-sm mt-4')
        
        ui.button('Login', on_click=lambda: check_input(input_box.value)).classes('mt-4 text-white')