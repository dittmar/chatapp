from os import urandom
from hashlib import scrypt

# Derive a key from the password and salt to store in the database and test passwords for correctness
def generate_key(password: str, salt: str) -> bytes:
    iterations = 16384
    block_size = 8
    parallelization_factor = 1
    return scrypt(password=password.encode(), salt=salt, n=iterations, r=block_size, p=parallelization_factor)

def generate_salt() -> bytes:
    return urandom(32)