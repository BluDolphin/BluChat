import json
from functions.encryption_functions import encrypt_data, decrypt_data

# RETURN CODES
# 1 for already there
# 2 for not there

# Data stored in list of dictionaries
# [{"active": True, "number": {"nonce":"encrypted_number"}}, {"active": False, "number": {"nonce":"encrypted_number"}}]

def load_numbers(key):
    stored_numbers = []
    
    with open('data/authorised_numbers.txt', 'r') as f:
        # Try and get data
        try:
            phone_data = json.load(f)

            for item in phone_data:
                # Decrypt encrypted dict key "number"
                decrypted_number = decrypt_data(item["number"], key) # Pass encrypted number and key
                stored_numbers.append({"active": item["active"], "number": decrypted_number}) # Append decrypted number with active status
                
        # If fail then assume empty
        except json.JSONDecodeError:
            print("Error decoding JSON from authorised_numbers.txt")
        
    return stored_numbers

    
def add_number(number, key):  
    # Load existing numbers
    stored_numbers = load_numbers(key)

    # Check if number already exists (uses encrypted check)
    if check_number(number, stored_numbers) == True:
        return 1
    
    # Encrypt number
    encrypted_number = encrypt_data(number, key) # Encrypt number
    
    # Append to end of list 
    with open('data/authorised_numbers.txt', 'r') as f: 
        encryted_data = json.load(f) # Load existing encrypted data 
    encryted_data.append({"active": True, "number": encrypted_number}) # Add new number
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(encryted_data, f) # Save updated encrypted data
    
    stored_numbers.append({"active": True, "number": number})
    return stored_numbers


def remove_number(number, key):       
    stored_numbers = load_numbers(key) # Load existing numbers
    with open('data/authorised_numbers.txt', 'r') as f: 
        encrypted_data = json.load(f) # Load existing encrypted data
    
    # Find index of number list 
    index = -1 # set index as not found
    for i, item in enumerate(stored_numbers): 
        if item["number"] == number:
            index = i
            break
    
    # Remove number from list
    stored_numbers.pop(index)
    encrypted_data.pop(index)
    
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(encrypted_data, f)
    
    return stored_numbers


def toggle_number(number, key): 
    stored_numbers = load_numbers(key)
    with open('data/authorised_numbers.txt', 'r') as f: 
        encrypted_data = json.load(f) # Load existing encrypted data
    
    
    # Find index of number list 
    index = -1 # set index as not found
    for i, item in enumerate(stored_numbers): 
        if item["number"] == number:
            index = i
            break
        
    # If number not found, return the original list
    if index == -1:
        return 2
    
    # Toggle the boolean value
    stored_numbers[index]["active"] = not stored_numbers[index]["active"]
    encrypted_data[index]["active"] = not encrypted_data[index]["active"]
    
    # Save the updated list to the file
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(encrypted_data, f)
    
    return stored_numbers


def check_number(number, stored_numbers):    
    # Check if number exists (convert both to string to be safe)
    if any(str(d["number"]).strip() == str(number).strip() for d in stored_numbers):
        return True
    else:
        return False
