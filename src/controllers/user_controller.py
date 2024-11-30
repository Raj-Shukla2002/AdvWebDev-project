# Import necessary modules and functions
from flask import jsonify, request, redirect, Blueprint  # Flask utilities for HTTP requests, responses, and route management
from src.models.models import db, User  # Database and User model
from src.config import hash_password, verify_password, create_jwt, decode_jwt  # Utility functions for security and token management
import requests  # For making HTTP requests to external APIs

# Create a Blueprint for user-related routes to organize them modularly
user_routes = Blueprint('user_routes', __name__)

# OAuth configuration for GitHub
CLIENT_ID = 'Ov23liIVtcQCU1iMLiiU'
CLIENT_SECRET = '25a2340208e05a66203b3ca38e69ca592e930244'
AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'  # GitHub OAuth authorization URL
TOKEN_URL = 'https://github.com/login/oauth/access_token'  # GitHub OAuth token URL
USER_API_URL = 'https://api.github.com/user'  # GitHub API URL to fetch user information
REDIRECT_URI = 'http://localhost:5000/callback'  # Callback URL for OAuth

# Route to initiate GitHub login
@user_routes.route('/login-with-github', methods=['GET'])
def login_with_github():
    """
    Redirect the user to GitHub's OAuth authorization page.
    """
    github_auth_url = f"{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user"
    return redirect(github_auth_url)

# Callback route to handle GitHub's response after user authentication
@user_routes.route('/callback', methods=['GET'])
def callback():
    """
    Handle the OAuth callback by exchanging the authorization code for an access token.
    Retrieve or register the user based on their GitHub profile.
    """
    code = request.args.get('code')  # Extract authorization code from the callback
    token_request_data = {  # Data for the token exchange request
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Accept': 'application/json'}
    response = requests.post(TOKEN_URL, data=token_request_data, headers=headers)  # Exchange code for access token
    token_response_data = response.json()
    access_token = token_response_data.get('access_token')

    if access_token:
        # Fetch user info from GitHub API using the access token
        user_info = get_github_user_info(access_token)
        username = user_info['login']

        # Register the user if they don't already exist in the database
        if not User.query.filter_by(username=username).first():
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()

        # Generate a JWT for the authenticated user
        token = create_jwt(username)
        return jsonify({
            "message": f"Welcome, {username}! You have successfully logged in using GitHub OAuth.",
            "token": token
        }), 200

    # If access token is missing or invalid, return an error
    return jsonify({"message": "Login failed"}), 400

# Function to fetch GitHub user info given an access token
@user_routes.route('/get_github', methods=['GET'])
def get_github_user_info(token):
    """
    Fetch user information from GitHub using the access token.
    """
    headers = {'Authorization': f'token {token}'}
    user_info_response = requests.get(USER_API_URL, headers=headers)
    return user_info_response.json() if user_info_response.status_code == 200 else None

# Route to register a new user
@user_routes.route('/register', methods=['POST', 'OPTIONS'])
def register_user():
    """
    Register a new user by storing their hashed password and username in the database.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    # Hash the password and save the user
    hashed_password, salt = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password, salt=salt)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200

# Route to log in an existing user
@user_routes.route('/login', methods=['POST'])
def login_user():
    """
    Authenticate an existing user and return a JWT for session management.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()

    # Retrieve user from the database
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Verify the password
    if verify_password(password, user.hashed_password, user.salt):
        token = create_jwt(username)  # Generate JWT
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid password"}), 400

# Route to delete a user
@user_routes.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user from the database after verifying their authorization.
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token is missing"}), 401

    # Decode the JWT token
    decoded_token = decode_jwt(token)
    if not decoded_token:
        return jsonify({"error": "Invalid or expired token"}), 401

    username = decoded_token.get('sub')

    # Retrieve the user to delete
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    # Ensure the requesting user is authorized to delete the user
    if username != user_to_delete.username:
        return jsonify({"error": "You are not authorized to delete this user"}), 403

    # Delete the user and commit changes
    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": f"User '{user_to_delete.username}' has been deleted successfully"}), 200

# Route to fetch all users
@user_routes.route('/users', methods=['GET'])
def get_users():
    """
    Fetch all users from the database and return them as a list.
    """
    try:
        # Query all users
        users = User.query.all()

        # Convert users to a dictionary format
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at.isoformat() if hasattr(user, "created_at") else None
            }
            for user in users
        ]

        return jsonify({"users": user_list}), 200

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500
