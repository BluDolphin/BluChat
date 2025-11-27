import os, hmac, hashlib

def check_hash(inputed_password):
    inputed_password = inputed_password.encode('utf-8')
    
    # Read browser key for salting
    if os.path.exists('data/crypt_data.txt'):
        with open('data/crypt_data.txt', 'r') as f:
            browser_key = f.readlines()[0].strip().encode('utf-8')
    
    # Re-hash inputed password with correct salt
    hashed_input = hmac.new(inputed_password, browser_key, hashlib.sha512).digest().hex()

    # Read stored password
    with open("data/crypt_data.txt", "r") as f:
        stored_password = f.readlines()[1].strip()
            
    # Check if inputed password matches stored password
    return hashed_input == stored_password # Return boolean

def hash_password(user_input):
    # use browser key as a salt
    with open('data/crypt_data.txt', 'r') as f:
        browser_key = f.read().strip().encode('utf-8')
    
    # Hash the inputed password
    hash = hmac.new(user_input, browser_key, hashlib.sha512).digest() 
    return hash

# TODO: sort this out 
def encrypt_data(data, key, salt):
    # Symetric encryption of data using AES-256 with HMAC-SHA512 key derivation
    
    # Key is password
    # Salt is browser key
    
    # Create HMAC object with key and salt
    hmac_key = hmac.new(salt.encode('utf-8'), key.encode('utf-8'), hashlib.sha512)
    
    return 

data = "test"
key = "key"
salt = "salt"

print(encrypt_data(data, key, salt))
print(encrypt_data(data, key, salt))
print(encrypt_data(data, key, salt))