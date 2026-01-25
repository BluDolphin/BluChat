from os import name
import json
from nicegui import ui, app
from functions.group_functions import create_group, get_group_names, load_all_groups, group_toggle_blocked, group_edit_instructions, delete_group, group_edit_model
from functions.config_functions import get_config
from pages.theme import frame
from functions.phonenumber_functions import load_numbers, add_number, remove_number, toggle_number, change_identifier, change_group
from functions.check_timeout import check_timeout
from functions.llm_functions import get_llm_usabilities


SETTING_BOX_COLOUR = '0F132D'

def content():
    def number_add_value(number, identifier=''):
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
        result = add_number(number, app.storage.tab.get('password'), identifier)
        
        # If number already exists
        if result == 1:
            ui.notify('Number already exists', color='orange')
            return

        number_table.rows = result # Update table rows
        new_number_input.value = ''  # Clear input field after adding
        ui.notify('Number added successfully', color='green')
    
    def number_remove_value(number):
        check_timeout(True) # Check for session timeout & reset timer
        # Remove number and get updated list
        stored_numbers = remove_number(number, app.storage.tab.get('password')) 
        number_table.rows = stored_numbers # Update table rows
    
    def number_toggle_value(row):  
        check_timeout(True) # Check for session timeout & reset timer
        # Toggle blocked status and update table
        toggle_number(row['number'], app.storage.tab.get('password'))

    def number_save_identifier(row):
        check_timeout(True) # Check for session timeout & reset timer
        
        # Update identifier for the number
        change_identifier(row['number'], row['identifier'], app.storage.tab.get('password'))

    def number_change_group(row):
        check_timeout(True) # Check for session timeout & reset timer
        # Change group for the number and refresh table
        change_group(row['number'], row['group'], app.storage.tab.get('password'))
        number_table.rows = load_numbers(app.storage.tab.get('password'))

    
    def group_add_value(group_name):
        check_timeout(True) # Check for session timeout & reset timer
        nonlocal stored_groups
        
        # Check for empty group name
        if not group_name.strip():
            ui.notify('Group name cannot be empty', color='red')
            return
        
        # Add group and update table
        result = create_group(group_name.strip(), app.storage.tab.get('password'))
        
        # If group already exists
        if result == 1:
            ui.notify('Group already exists', color='orange')
            return

        new_group_input.value = ''  # Clear input field after adding
        
        # Reload groups and numbers after adding a group
        stored_groups = parse_stored_groups(result)
        group_table.rows = stored_groups # Update table rows
        refresh_group_list() # Update available group names in number table dropdowns
        ui.notify('Group added successfully', color='green')

    def group_remove_value(group_name):
        check_timeout(True) # Check for session timeout & reset timer
        nonlocal stored_groups

        # Load current numbers
        stored_numbers = load_numbers(app.storage.tab.get('password'))
        
        # Attempt deletion and handle not-found
        result = delete_group(group_name, app.storage.tab.get('password'))
        if result == 1:
            ui.notify('Group not found (already deleted?)', color='red')
            return

        # Update stored_groups with returned dict
        stored_groups = result

        # For each number that was in the removed group, set to 'None'
        for number in list(stored_numbers):
            if number.get('group') == group_name:
                stored_numbers = change_group(number['number'], 'None', app.storage.tab.get('password'))

        # Update both tables with new data
        number_table.rows = stored_numbers
        group_table.rows = parse_stored_groups(stored_groups)

        # Update available group names in number table dropdowns
        refresh_group_list()
         
    def group_toggle_value(row):
        check_timeout(True) # Check for session timeout & reset timer
        # Toggle blocked status and update table
        group_toggle_blocked(row['group_name'])
    
    def group_model_change(row):
        check_timeout(True) # Check for session timeout & reset timer
        # Update group model
        group_edit_model(row['group_name'], row['model'].lower())
    
    def group_instructions_change(row, new_instructions):
        check_timeout(True) # Check for session timeout & reset timer
        # Update group instructions
        group_edit_instructions(row['group_name'], new_instructions, app.storage.tab.get('password'))

    def refresh_group_list():
        nonlocal stored_groups, stored_numbers
        
        # Reload the latest data
        stored_groups = parse_stored_groups(load_all_groups(app.storage.tab.get('password')))
        stored_numbers = load_numbers(app.storage.tab.get('password'))

        group_list = json.dumps(get_group_names(stored_groups, stored_numbers))
        
        # Replace slot in number table for group selection dropdown
        number_table.add_slot('body-cell-group', f'''
        <q-td :props='props'>
            <q-select dense
                v-model='props.row.group'
                :options='{group_list}'
                class='w-24'
                @update:model-value='$parent.$emit('change_group', props.row)' />
        </q-td>
        ''')
        
        # Force table refresh
        number_table.rows = stored_numbers
        group_table.rows = stored_groups
        
    
    # Handler to parse stored groups dict into list of dicts for table
    def parse_stored_groups(raw_stored_groups):
        stored_groups = []
        # for each group in raw_stored_groups dict
        for group_name, data in raw_stored_groups.items():
            # Append to list of dicts (same format as phone numbers)
            stored_groups.append({
                'group_name': group_name,
                'blocked': data['blocked'],
                'model': data['model'].capitalize(),
                'llm_instructions': data['llm_instructions']
            })
            
        return stored_groups

    # Define table columns
    # Works by name = field in row dict, label is header text, field = key in row dict
    phone_columns = [
    {'name': 'blocked', 'label': 'Blocked', 'field': 'blocked'},
    {'name': 'number', 'label': 'Number', 'field': 'number'},
    {'name': 'identifier', 'label': 'Identifier', 'field': 'identifier'},
    {'name': 'group', 'label': 'Group', 'field': 'group'},
    {'name': 'remove', 'label': 'Remove', 'field': 'remove'},
    ]  
    
    group_columns = [
    {'name': 'group_name', 'label': 'Group Name', 'field': 'group_name'},
    {'name': 'blocked', 'label': 'Blocked', 'field': 'blocked'},
    {'name': 'model', 'label': 'Model', 'field': 'model'},
    {'name': 'llm_instructions', 'label': 'Instructions', 'field': 'llm_instructions'},
    {'name': 'remove', 'label': 'Remove', 'field': 'remove'},
    ]
    
    # Load initial data
    stored_numbers = load_numbers(app.storage.tab.get('password'))
    stored_groups_raw = load_all_groups(app.storage.tab.get('password'))

    # Parse stored groups into list of dicts for table
    stored_groups = parse_stored_groups(stored_groups_raw)

    usable_llms = get_llm_usabilities()

    with frame('Whitelist'):
        ui.label('Manage phone numbers and groupings').classes('text-2xl mt-2')
        
        with ui.row().classes('my-4'):
            with ui.card().classes('min-w-[570px] h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('Add and configure phone numbers').classes('text-lg mb-2 underline')
                with ui.row().classes('w-full items-center'):
                    new_number_input = ui.input(label='Phone Number').props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-48')
                    new_identifier_input = ui.input(label='Identifier (optional)').props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-48 ml-4')
                    ui.button('Add', on_click=lambda: number_add_value(new_number_input.value, new_identifier_input.value)).classes('ml-4')
                    
                for column in phone_columns:
                    column['align'] = 'center'
                number_table = ui.table(columns=phone_columns, rows=stored_numbers)

            with ui.card().classes('min-w-[775px] h-auto').style(f'background-color: #{SETTING_BOX_COLOUR}'):
                ui.label('Add and manage groups').classes('text-lg mb-2 underline')
                with ui.row().classes('w-full items-center'):
                    new_group_input = ui.input(label='Group Name').props('underline dark color="dark-gray" input-style="color: white" label-color="white"').classes('w-48')
                    ui.button('Add', on_click=lambda: group_add_value(new_group_input.value)).classes('ml-4')    
                                
                for column in group_columns:
                    column['align'] = 'center'
                group_table = ui.table(columns=group_columns, rows=stored_groups)



        # ===== Whitelist table custom slots =====
        # Add toggle to each row of the blocked column
        # If the global whitelist is disabled, show the blocked column faded and non-interactive, with a tooltip on hover
        if get_config('global_whitelist'):
            number_table.add_slot('body-cell-blocked', ''' 
            <q-td :props="props">
                <div>
                    <q-toggle v-model="props.row.blocked" 
                    @update:model-value="$parent.$emit('toggle_blocked', props.row)" />
                    <q-tooltip anchor="top middle">Click to toggle blocked</q-tooltip>
                </div>
            </q-td>
            ''')
        else:
            number_table.add_slot('body-cell-blocked', '''
            <q-td :props="props" style="opacity: .45;">
                <div style="pointer-events: auto; display: inline-flex; align-items: center;">
                    <q-toggle v-model="props.row.blocked" disable />
                    <q-tooltip anchor="top middle">Global whitelist is disabled — enable in Settings to use blocked toggles</q-tooltip>
                </div>
            </q-td>
            ''')
        
        # Add text input for identifier column
        number_table.add_slot('body-cell-identifier', '''
        <q-td :props="props">
            <q-input dense
                v-model="props.row.identifier"
                class="w-28"
                @blur="$parent.$emit('save_identifier', props.row)" />
        </q-td>
        ''')
        
        # Add dropdown for group selection
        group_list = json.dumps(get_group_names(stored_groups, stored_numbers))
        number_table.add_slot('body-cell-group', f'''
        <q-td :props="props">
            <q-select dense
                v-model="props.row.group"
                :options='{group_list}'
                class="w-24"
                @update:model-value="$parent.$emit('change_group', props.row)" />
        </q-td>
        ''')
        
        # Add button to each row of the remove column
        number_table.add_slot('body-cell-remove', '''
        <q-td :props="props">
            <q-btn label="Remove" 
            @click="$parent.$emit('remove_action', props.row)" flat />
        </q-td>
        ''')
        
        
        # ===== Group table custom slots =====
        # Add toggle for blocked
        group_table.add_slot('body-cell-blocked', ''' 
        <q-td :props="props">
            <q-toggle v-model="props.row.blocked" 
            @update:model-value="$parent.$emit('toggle_blocked', props.row)" />
        </q-td>
        ''')
        
        # Add text area for llm_instructions
        group_table.add_slot('body-cell-llm_instructions', '''
        <q-td :props="props">
            <q-input dense
                type="textarea"
                autogrow
                v-model="props.row.llm_instructions"
                class="w-56"
                rows="2"
                @blur="$parent.$emit('edit_instructions', props.row)" />
        </q-td>
        ''')
        
        # Add dropdown for model selection
        group_table.add_slot('body-cell-model', f'''
        <q-td :props="props">
            <q-select dense
                v-model="props.row.model"
                :options='{json.dumps(usable_llms)}'
                class="w-24"
                @update:model-value="$parent.$emit('change_model', props.row)" />
        </q-td>
        ''')
        
        # Add button to each row of the remove column
        group_table.add_slot('body-cell-remove', '''
        <q-td :props="props">
            <q-btn label="Remove" 
            @click="$parent.$emit('remove_action', props.row)" flat />
        </q-td>
        ''')
        
        
        # Mini functions for toggle and remove
        number_table.on('toggle_blocked', lambda e: number_toggle_value(e.args))
        number_table.on('save_identifier', lambda e: number_save_identifier(e.args))
        number_table.on('change_group', lambda e: number_change_group(e.args))
        number_table.on('remove_action', lambda e: number_remove_value(e.args['number']))

        
        group_table.on('toggle_blocked', lambda e: group_toggle_value(e.args)) 
        group_table.on('change_model', lambda e: group_model_change(e.args))
        group_table.on('edit_instructions', lambda e: group_instructions_change(e.args, e.args['llm_instructions']))
        group_table.on('remove_action', lambda e: group_remove_value(e.args['group_name']))