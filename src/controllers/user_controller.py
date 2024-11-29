from flask import jsonify, request, redirect, Blueprint
from src.models.models import db, User
from src.config import hash_password, verify_password, create_jwt, decode_jwt
import requests

user_routes = Blueprint('user_routes', __name__)

CLIENT_ID = 'Ov23liIVtcQCU1iMLiiU'
CLIENT_SECRET = '25a2340208e05a66203b3ca38e69ca592e930244'
AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
USER_API_URL = 'https://api.github.com/user'
REDIRECT_URI = 'http://localhost:5000/callback'

@user_routes.route('/login-with-github', methods=['GET'])
def login_with_github():
    github_auth_url = f"{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user"
    return redirect(github_auth_url)

@user_routes.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_request_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    headers = {'Accept': 'application/json'}
    response = requests.post(TOKEN_URL, data=token_request_data, headers=headers)
    token_response_data = response.json()
    access_token = token_response_data.get('access_token')

    if access_token:
        user_info = get_github_user_info(access_token)
        username = user_info['login']

        if not User.query.filter_by(username=username).first():
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()

        token = create_jwt(username)
        return jsonify({
            "message": f"Welcome, {username}! You have successfully logged in using GitHub OAuth.",
            "token": token
        }), 200

    return jsonify({"message": "Login failed"}), 400

@user_routes.route('/get_github', methods=['GET'])
def get_github_user_info(token):
    headers = {'Authorization': f'token {token}'}
    user_info_response = requests.get(USER_API_URL, headers=headers)
    return user_info_response.json() if user_info_response.status_code == 200 else None

@user_routes.route('/register', methods=['POST', 'OPTIONS'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password, salt = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password, salt=salt)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200

@user_routes.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    if verify_password(password, user.hashed_password, user.salt):
        token = create_jwt(username)
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid password"}), 400


@user_routes.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token is missing"}), 401

    decoded_token = decode_jwt(token)
    if not decoded_token:
        return jsonify({"error": "Invalid or expired token"}), 401

    username = decoded_token.get('sub')

    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    if username != user_to_delete.username:
        return jsonify({"error": "You are not authorized to delete this user"}), 403

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": f"User '{user_to_delete.username}' has been deleted successfully"}), 200


@user_routes.route('/users', methods=['GET'])  # Add this

def get_users():
    """
    Fetch all users from the database.
    """
    try:
        # Query all users
        users = User.query.all()

        # Create a list of user dictionaries
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
        return jsonify({"error": str(e)}), 500