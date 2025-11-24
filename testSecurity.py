import hashlib
import hmac


# =================================== method 1 ===================================
key = "hashkey".encode('utf-8') # STORED SECURELY SOMEWHERE
data = "phonenumber".encode('utf-8') # USER INPUT
salt = "somesalt".encode('utf-8') # STORED SECURELY SOMEWHERE + Unique per user

# Create HMAC using SHA512
h = hmac.new(key, data, hashlib.sha512)

# Take the first 8 bytes of the HMAC digest
hmac_bytes = h.digest()[:8]

# Hash the 8 bytes combined with salt using SHA256
final_hash = hashlib.sha512(hmac_bytes + salt).hexdigest()

print(f"HMAC (first 8 bytes): {hmac_bytes.hex()}")
print(f"Final Hash (HMAC+Salt): {final_hash}")


# =================================== method 2 ===================================
key = "hashkey".encode('utf-8') # STORED SECURELY SOMEWHERE
data = "phonenumber".encode('utf-8') # USER INPUT

h = hmac.new(key, data, hashlib.sha512)

hmac_bytes = h.digest()

print(f"HMAC (hex): {hmac_bytes.hex()}")