import os, hmac, hashlib

def check_password(inputed_password):
    inputed_password = inputed_password.encode('utf-8')
    
    # Read browser key for salting
    if os.path.exists('data/browser_key.txt'):
        with open('data/browser_key.txt', 'r') as f:
            browser_key = f.read().strip().encode('utf-8')
    
    # Re-hash inputed password with correct salt
    hashed_input = hmac.new(inputed_password, browser_key, hashlib.sha512).digest()
    
    # Read stored password
    if os.path.exists("data/config.txt"):
        with open("data/config.txt", "r") as f:
            stored_password = f.readline().strip()
            
    # Check if inputed password matches stored password
    return hashed_input.hex() == stored_password # Return boolean