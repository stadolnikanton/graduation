import hashlib


def hash_password(password):
    hashed_string = hashlib.sha256(password.encode()).hexdigest()
    return hashed_string
