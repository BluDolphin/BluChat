import json
from functions.config_functions import get_config
from functions.encryption_functions import encrypt_data, decrypt_data
from functions.group_functions import check_group_exists

# RETURN CODES
# 1 for already there
# 2 for not there
# 3 for invalid group

# Data stored in list of dictionaries
# blocked: bool (is number blocked)
# number: encrypted string (encrypted phone number)
# identifier: str (optional identifier for number)
# group: str (group name)

# Load all numbers 
def load_numbers(key):
    stored_numbers = []
    
    with open('data/authorised_numbers.json', 'r') as f:
        # Try and get data
        try:
            phone_data = json.load(f)

            for item in phone_data:
                # Decrypt encrypted dict key 'number'
                decrypted_number = decrypt_data(item['number'], key) # Pass encrypted number and key
                stored_numbers.append({'blocked': item['blocked'], # Append decrypted number with blocked status
                                       'number': decrypted_number, 
                                       'identifier': item['identifier'], 
                                       'group': item['group']}) 
                
        # If fail then assume empty
        except json.JSONDecodeError:
            print('Error decoding JSON from authorised_numbers.json')
        
    return stored_numbers


# Add number
def add_number(number, key, identifier='', group='None'): 
    # Load existing numbers
    stored_numbers = load_numbers(key)

    # Check if number already exists (uses encrypted check)
    if check_number_exists(number, stored_numbers) == True:
        return 1
    
    # Encrypt number
    encrypted_number = encrypt_data(number, key) # Encrypt number
    
    # Append to end of list 
    try:
        with open('data/authorised_numbers.json', 'r') as f: 
            encrypted_data = json.load(f) # Load existing encrypted data 
    except (json.JSONDecodeError, FileNotFoundError):
        encrypted_data = []
        
    encrypted_data.append({'blocked': True, 
                          'number': encrypted_number,
                          'identifier': identifier,
                          'group': group}) # Add new number
    
    with open('data/authorised_numbers.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4) # Save updated encrypted data
    
    stored_numbers.append({'blocked': True, 'number': number, 'identifier': identifier, 'group': group}) # Add new number to decrypted list
    return stored_numbers # Return updated (decrypted) list


# Remove number
def remove_number(number, key):       
    stored_numbers = load_numbers(key) # Load existing numbers
    
    # Try load data
    try:
        with open('data/authorised_numbers.json', 'r') as f: 
            encrypted_data = json.load(f) # Load existing encrypted data
    except (json.JSONDecodeError, FileNotFoundError):
        return stored_numbers
    
    # Find index of number list 
    index = get_number_index(number, stored_numbers)
        
    # Remove number from list
    encrypted_data.pop(index)
    stored_numbers.pop(index)

    
    with open('data/authorised_numbers.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4) # Save updated encrypted data
    
    return stored_numbers


# Toggle number blocked/inblocked
def toggle_number(number, key): 
    stored_numbers = load_numbers(key)
    try:
        with open('data/authorised_numbers.json', 'r') as f: 
            encrypted_data = json.load(f) # Load existing encrypted data
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    
    # Find index of number list 
    index = get_number_index(number, stored_numbers)
        
    # If number not found, return the original list
    if index == -1:
        return 2
    
    # Toggle the boolean value
    stored_numbers[index]['blocked'] = not stored_numbers[index]['blocked']
    encrypted_data[index]['blocked'] = not encrypted_data[index]['blocked']
    
    # Save the updated list to the file
    with open('data/authorised_numbers.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
    
    return stored_numbers


# Edit numbers text identifier (human readable string)
def change_identifier(number, new_identifier, key): 
    stored_numbers = load_numbers(key) # Load decrypted numbers for searching
    
    try:
        with open('data/authorised_numbers.json', 'r') as f: 
            encrypted_data = json.load(f) # Load existing encrypted data
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    # Find index of number list 
    index = get_number_index(number, stored_numbers)
        
    # If number not found, return the original list
    if index == -1:
        return 2
    
    # Update the identifier
    encrypted_data[index]['identifier'] = new_identifier
    
    # Save the updated list to the file
    with open('data/authorised_numbers.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
    
    return 


# Edit group of number
def change_group(number, new_group, key): 
    if check_group_exists(new_group) == False and new_group != 'None': # If group does not exist or new group is empty
        return 3 # Return error code 3 for invalid group
    
    stored_numbers = load_numbers(key) # Load decrypted numbers for searching

    try:
        with open('data/authorised_numbers.json', 'r') as f: 
            encrypted_data = json.load(f) # Load existing encrypted data
    except (json.JSONDecodeError, FileNotFoundError):
        return 2
    
    
    # Find index of number list 
    index = get_number_index(number, stored_numbers)
        
    # If number not found, return the original list
    if index == -1:
        return 2
    
    # Update the group
    encrypted_data[index]['group'] = new_group
    stored_numbers[index]['group'] = new_group
    
    # Save the updated list to the file
    with open('data/authorised_numbers.json', 'w') as f:
        json.dump(encrypted_data, f, indent=4)
    
    return stored_numbers


# Function to check if sender is authorised
def check_sender_auth(sender, key, toggle):
    if toggle == False:
        return True
    
    authorized_numbers = load_numbers(key)
    country_code = get_config('country_code')
        
    for entry in authorized_numbers:
        # Convert number to international format
        if not entry['number'].startswith('+'):
            entry['number'] = entry['number'][1:] # Cut first number 
            entry['number'] = country_code + entry['number']  # Convert to international format
        
        if entry['number'] == sender and entry['blocked']:
            return True
            
    return False


# Check if number exists in stored numbers list
def check_number_exists(number, stored_numbers):    
    # Check if number exists (convert both to string to be safe)
    if any(str(d['number']).strip() == str(number).strip() for d in stored_numbers):
        return True
    else:
        return False


# Get index of number in stored numbers list
def get_number_index(number, data_dict):
    for i, item in enumerate(data_dict): 
        if item['number'] == number:
            return i
    return -1
