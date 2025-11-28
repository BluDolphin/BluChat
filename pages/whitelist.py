from nicegui import ui, app
from pages.theme import frame
from functions.phonenumber_functions import load_numbers, add_number, remove_number, toggle_number
from functions.check_timeout import check_timeout

def content():
    def add_value(number):
        check_timeout(True) # Check for session timeout & reset timer
        # Check for a number 
        if not number.isdigit():
            ui.notify('Not a number', color='red')
            return
        # Check for length
        if not 10 < len(number) < 14:
            ui.notify('Number length must be between 11 and 13 digits', color='red')
            return
        
        # Add number and update table
        result = add_number(number, app.storage.tab.get('password'))
        
        # If number already exists
        if result == 1:
            ui.notify('Number already exists', color='orange')
            return

        table.rows = result # Update table rows
        new_number_input.value = ''  # Clear input field after adding
        ui.notify('Number added successfully', color='green')
    
    def remove_value(number):
        check_timeout(True) # Check for session timeout & reset timer
        # Remove number and get updated list
        stored_numbers=remove_number(number, app.storage.tab.get('password')) # 
        table.rows = stored_numbers # Update table rows

    def toggle_value(row):
        check_timeout(True) # Check for session timeout & reset timer
        # Toggle active status and update table
        toggle_number(row['number'], app.storage.tab.get('password'))

    
    columns = [
    {'name': 'active', 'label': 'active', 'field': 'active'},
    {'name': 'number', 'label': 'number', 'field': 'number'},
    {'name': 'action', 'label': 'Action', 'field': 'action'},
    ]  
    
    # Load initial data
    stored_numbers = load_numbers(app.storage.tab.get('password'))

    
    with frame('Whitelist'):
        ui.label('Manage whitelisted phone numbers').classes('text-2xl mt-2')
        #TODO: FIX INPUT SHOWING ENCRYPTED BEFORE REFRESH
        with ui.row().classes('w-full items-center'):
            new_number_input = ui.input(label='Phone Number').props('input-style="color: white" label-color="white"').classes('w-64')
            ui.button('Add', on_click=lambda: add_value(new_number_input.value)).classes('ml-4')
            
        
        for column in columns:
            column['align'] = 'center'
        table = ui.table(columns=columns, rows=stored_numbers)


        # Add switch to active column
            # In column active
        table.add_slot('body-cell-active', ''' 
        <q-td :props="props">
            <q-toggle v-model="props.row.active" @update:model-value="$parent.$emit('toggle_active', props.row)" />
        </q-td>
        ''')
        
        # Add button to each row
        table.add_slot('body-cell-action', '''
        <q-td :props="props">
            <q-btn label="Remove" @click="$parent.$emit('click_action', props.row)" flat />
        </q-td>
        ''')
        
        # Mini functions for toggle and remove
        table.on('toggle_active', lambda e: toggle_value(e.args))
        table.on('click_action', lambda e: remove_value(e.args['number']))