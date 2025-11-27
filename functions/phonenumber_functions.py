import json

# RETURN CODES
# 1 for already there
# 2 for not there

def load_numbers():
    with open('data/authorised_numbers.txt', 'r') as f:
        stored_numbers = json.load(f)
        
    return stored_numbers

def add_number(number, stored_numbers):    
    # Check if number already exists
    if [True, number] and [False, number] in stored_numbers:
        return 1
    
    # Add number to list
    stored_numbers.append([True, number])
    
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers

def remove_number(number, stored_numbers):       
    # Check if number exists
    if not [True, number] and not [False, number] in stored_numbers:
        return 1
    
    # Find index of number list 
    try:
        index = stored_numbers.index([False, number])
    except ValueError:
        index = stored_numbers.index([True, number])
    
    # Remove number from list
    stored_numbers.pop(index)
    
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers
    

def toggle_number(number, stored_numbers): 
    # Find index of number list 
    index = -1 # set index as not found
    for i, item in enumerate(stored_numbers): 
        if item[1] == number:
            index = i
            break
        
    # If number not found, return the original list
    if index == -1:
        return 2
    
    # Toggle the boolean value
    stored_numbers[index][0] = not stored_numbers[index][0]
    
    # Save the updated list to the file
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers