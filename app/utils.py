from pwdlib import PasswordHash

# Initialize a recommended password hashing instance
_password_hasher = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using a secure algorithm.
    Args:
        password (str): The plain-text password to hash.
    Returns:
        str: The hashed password.
    """
    return _password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hashed version.
    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The stored hashed password to compare against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return _password_hasher.verify(plain_password, hashed_password)