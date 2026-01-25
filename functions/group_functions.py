'''[{
        'GROUP_NAME': {
            'blocked': BOOLEAN,
            'model': STR,
            'llm_instructions': ENCRYPTED_STR
        }
    }]
'''
from functions.encryption_functions import encrypt_data, decrypt_data
from functions.config_functions import get_config
import json

# Load group data
def load_all_groups(key=None):
    if key is None:
        with open('data/group_list.json', 'r') as f:
            try:
                stored_groups = json.load(f)
            except json.JSONDecodeError:
                stored_groups = {}
    else:
        with open('data/group_list.json', 'r') as f:
            try:
                stored_groups = json.load(f)
                for group in stored_groups:
                    # Decrypt llm_instructions for each group
                    group_instructions_encrypted = stored_groups[group]['llm_instructions']
                    decrypted_instructions = decrypt_data(group_instructions_encrypted, key)
                    stored_groups[group]['llm_instructions'] = decrypted_instructions 
            except json.JSONDecodeError:
                stored_groups = {}
            
    return stored_groups

# Create new group
def create_group(group_name, key):
    # Get default model and instructions from config
    stored_default_model = get_config('active_llm')
    stored_default_instructions = get_config('prompt_instructions')
    decrypted_default_instructions = decrypt_data(stored_default_instructions, key)
    
    
    # Load existing groups
    stored_groups = load_all_groups(key)
    
    # Check if group name already exists
    if group_name in stored_groups:
        return 1 # Error code 1 for already exists
    
    new_group_data = {
        'blocked': False,
        'model': stored_default_model,
        'llm_instructions': decrypted_default_instructions
    }
    
        
    # Add new group to stored groups
    stored_groups[group_name] = new_group_data
    
    with open('data/group_list.json', 'w') as f:
        json.dump(stored_groups, f, indent=4)
    
    return stored_groups # Return updated group list


# Delete group
def delete_group(group_name, key):
    stored_groups = load_all_groups(key)
    
    # Filter out the group to be deleted
    if group_name in stored_groups:
        del stored_groups[group_name]
    else:
        return 1 # Error code 1 for not found
    
    with open('data/group_list.json', 'w') as f:
        json.dump(stored_groups, f, indent=4)
    
    return stored_groups # Return updated group list


# Edit group value 
def group_toggle_blocked(group_name):
    stored_groups = load_all_groups()
    try:
        with open('data/group_list.json', 'r') as f:
            encrypted_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    if group_name in stored_groups:
        encrypted_data[group_name]['blocked'] = not encrypted_data[group_name]['blocked']
    else:
        return 1 # Error code 1 for not found
    
    with open('data/group_list.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
        
    return 


# Edit stored model for group
def group_edit_model(group_name, new_model):
    stored_groups = load_all_groups()
    stored_llm_configs = get_config('llm_configs')
    
    try:
        with open('data/group_list.json', 'r') as f:
            encrypted_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    
    # Check if new_model is in stored llm configs
    if f'{new_model}_config' not in stored_llm_configs:
        return 2 # Error code 2 for invalid model
    # Check if model is marked usable
    if stored_llm_configs[f'{new_model}_config'].get('usable') != True:
        return 3 # Error code 3 for not usable

    if group_name in stored_groups:
        encrypted_data[group_name]['model'] = new_model
    else:
        return 1 # Error code 1 for not found
    
    with open('data/group_list.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
    
    return 


# Edit stored LLM instructions for group
def group_edit_instructions(group_name, new_instructions, key):
    # Load existing groups encrypted as data will be replaced
    stored_groups = load_all_groups()
    
    try:
        with open('data/group_list.json', 'r') as f:
            encrypted_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    # encrypt new instructions before storing
    encrypted_instructions = encrypt_data(new_instructions, key)
    
    if group_name in stored_groups:
        encrypted_data[group_name]['llm_instructions'] = encrypted_instructions
    else:
        return 1 # Error code 1 for not found
    
    with open('data/group_list.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
    
    return 


# Check if group exists
def check_group_exists(group_name):
    stored_groups = load_all_groups()
    
    if group_name in stored_groups:
        return True
    
    return False

# Get list of group names
def get_group_names(stored_groups, stored_numbers):
    group_names = ['None']
    # For each stored group, add to list
    for group in stored_groups:
        group_names.append(group.get('group_name'))
    
    # For each number's group, add to list if not already present
    for number in stored_numbers:
        if number.get('group') not in group_names:
            group_names.append(number.get('group'))
    return group_names