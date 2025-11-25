import os, hmac, hashlib

def check_password(inputed_password):
    inputed_password = inputed_password.encode('utf-8')
    
    hashed_input = hmac.new(inputed_password, b"thisIsASalt", hashlib.sha512).digest()
    
    # If setup has been completed before, read stored password
    if os.path.exists("data/config.txt"):
        with open("data/config.txt", "r") as f:
            stored_password = f.readline().strip()
    
    # Check if inputed password matches stored password
    return hashed_input.hex() == stored_password # Return boolean