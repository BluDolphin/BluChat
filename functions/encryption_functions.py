import os, hmac, hashlib, secrets, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def check_hash(inputed_password):
    inputed_password = inputed_password.encode('utf-8')
    
    # Read browser key for salting
    if os.path.exists('data/crypt_data.json'):
        with open('data/crypt_data.json', 'r') as f:
            browser_key = json.load(f)['browser_key'].encode('utf-8')
    
    # Re-hash inputed password with correct salt
    hashed_input = hmac.new(inputed_password, browser_key, hashlib.sha512).digest().hex()

    # Read stored password
    with open("data/crypt_data.json", "r") as f:
        stored_password = json.load(f)['password']
            
    # Check if inputed password matches stored password
    return hashed_input == stored_password # Return boolean

def hash_password(user_input):
    # use browser key as a salt
    with open('data/crypt_data.json', 'r') as f:
        browser_key = json.load(f)['browser_key'].encode('utf-8')
    
    # Hash the inputed password
    hash = hmac.new(user_input, browser_key, hashlib.sha512).digest() 
    return hash

def encrypt_data(data, key):
    # Symetric encryption of data using AES-256 with HMAC-SHA512 key derivation
    # key(Password) and salt(browser_key) hashed for form encryption key
    
    with open('data/crypt_data.json', 'r') as f:
        salt = json.load(f)['browser_key']

    if isinstance(key, str):
        key = key.encode('utf-8')
        
    encryption_key = hmac.new(salt.encode('utf-8'), key, hashlib.sha512).digest()[:32] # AES-256 needs 32 bytes key
    nonce = secrets.token_bytes(24) # 192-bit nonce for AES-GCM

    ciphered_message = AESGCM(encryption_key).encrypt(nonce, data.encode('utf-8'), None)
    encrypted_message = f"{nonce.hex()}:{ciphered_message.hex()}"
    
    return encrypted_message

def decrypt_data(encrypted_data, key):  
    # Handle empty input 
    if encrypted_data == '' or encrypted_data is None:
        return ''
    
    with open('data/crypt_data.json', 'r') as f:
        salt = json.load(f)['browser_key']

    if isinstance(key, str):
        key = key.encode('utf-8')
        
    # Calculate encryption key
    encryption_key = hmac.new(salt.encode('utf-8'), key, hashlib.sha512).digest()[:32] # AES-256 needs 32 bytes key
    
    try:
        # Split nonce and ciphered message
        nonce_hex, ciphered_message_hex = encrypted_data.split(':')
        nonce = bytes.fromhex(nonce_hex) # Convert nonce back to bytes
        ciphered_message = bytes.fromhex(ciphered_message_hex) # Convert ciphered message back to bytes
    
        # Decrypt message
        decrypted_message = AESGCM(encryption_key).decrypt(nonce, ciphered_message, None).decode('utf-8')
        return decrypted_message
    except Exception as e: # Decryption failed
        return 1