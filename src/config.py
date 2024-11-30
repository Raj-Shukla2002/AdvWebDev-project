# Import necessary libraries
import jwt  # Library for encoding and decoding JSON Web Tokens (JWT)
import bcrypt  # Library for hashing and verifying passwords
from flask import current_app  # Provides access to the current Flask app context
import datetime  # Library for handling date and time operations

# A constant pepper value added to passwords for additional security
PEPPER = b'supersecretpepper'

# Function to hash a password with a unique salt
def hash_password(password):
    """
    Hashes a password with a unique salt and a pepper.

    Args:
        password (bytes): The plaintext password to be hashed.

    Returns:
        tuple: A tuple containing the hashed password and the salt used.
    """
    # Generate a random salt
    salt = bcrypt.gensalt()

    # Hash the password with the pepper and salt
    hashed_password = bcrypt.hashpw(password + PEPPER, salt)

    # Return the hashed password and the salt
    return hashed_password, salt

# Function to verify if a provided password matches a stored hashed password
def verify_password(password, stored_hashed_password, stored_salt):
    """
    Verifies a plaintext password against a stored hashed password.

    Args:
        password (bytes): The plaintext password to verify.
        stored_hashed_password (bytes): The stored hashed password.
        stored_salt (bytes): The salt used to hash the stored password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    # Hash the provided password with the stored salt and pepper
    hashed_password = bcrypt.hashpw(password + PEPPER, stored_salt)

    # Check if the hashed password matches the stored hashed password
    return hashed_password == stored_hashed_password

# Function to create a JSON Web Token (JWT) for a user
def create_jwt(username):
    """
    Creates a JSON Web Token (JWT) for a user.

    Args:
        username (str): The username to include in the token payload.

    Returns:
        str: The encoded JWT as a string.
    """
    # Define the token payload with subject, issued-at time, and expiration time
    payload = {
        'sub': username,  # The subject of the token (the username)
        'iat': datetime.datetime.utcnow(),  # Issued at current UTC time
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),  # Expires in 30 minutes
    }

    # Encode the payload with the app's secret key using the HS256 algorithm
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

# Function to decode and verify a JSON Web Token (JWT)
def decode_jwt(token):
    """
    Decodes a JSON Web Token (JWT) and verifies its validity.

    Args:
        token (str): The encoded JWT to decode.

    Returns:
        dict or None: The decoded payload if valid, or None if the token is invalid or expired.
    """
    try:
        # Decode the token using the app's secret key and HS256 algorithm
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        # Return None if the token has expired
        return None
    except jwt.InvalidTokenError:
        # Return None if the token is invalid
        return None
