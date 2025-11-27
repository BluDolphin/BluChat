import json

# RETURN CODES
# 1 for already there
# 2 for not there

# Data stored in list of dictionaries
# [{"active": True, "number": "+447123456789"}, {"active": False, "number": "+447987654321"}]

def load_numbers():
    with open('data/authorised_numbers.txt', 'r') as f:
        # Try and get data
        try:
            stored_numbers = json.load(f)
        
        # If fail then assume empty
        except json.JSONDecodeError:
            stored_numbers = []
        
    return stored_numbers

def add_number(number):  
    stored_numbers = load_numbers()
      
    # Check if number already exists
    if check_number(number) == True:
        return 1
    
    # Add number to list
    stored_numbers.append({"active": True, "number": number})
    
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers

def remove_number(number):       
    stored_numbers = load_numbers()
    
    # Find index of number list 
    index = -1 # set index as not found
    for i, item in enumerate(stored_numbers): 
        if item["number"] == number:
            index = i
            break
    
    # Remove number from list
    stored_numbers.pop(index)
    
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers
    
def toggle_number(number): 
    stored_numbers = load_numbers()
    
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
    
    # Save the updated list to the file
    with open('data/authorised_numbers.txt', 'w') as f:
        json.dump(stored_numbers, f)
    
    return stored_numbers

def check_number(number): 
    stored_numbers = load_numbers()
    
    # Check if number exists (convert both to string to be safe)
    if any(str(d["number"]).strip() == str(number).strip() for d in stored_numbers):
        return True
    else:
        return False