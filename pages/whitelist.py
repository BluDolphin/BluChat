from nicegui import ui
from pages.theme import frame
from functions.phonenumber_functions import load_numbers, add_number, remove_number, toggle_number

def content():
    def add_value(number):
        # Check for a number 
        if not number.isdigit():
            ui.notify('Not a number', color='red')
            return
        # Check for length
        if not 10 < len(number) < 14:
            ui.notify('Number length must be between 11 and 13 digits', color='red')
            return
        
        add_number(number, stored_numbers)
        
    # Load initial data
    stored_numbers = load_numbers()

    with frame('Whitelist'):
        ui.label('Manage whitelisted phone numbers').classes('text-2xl mt-2')
        with ui.row().classes('w-full items-center'):
            new_number_input = ui.input(label='Phone Number').props('input-style="color: white" label-color="white"').classes('w-64')
            ui.button('Add', on_click=lambda: add_value(new_number_input.value)).classes('ml-4')