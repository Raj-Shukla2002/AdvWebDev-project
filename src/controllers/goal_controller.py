# Import necessary modules and functions from Flask and other parts of the application
from flask import jsonify, request, current_app, Blueprint  # Flask utilities for handling HTTP requests and responses
from src.models.models import db, User, Goal, Workout  # Import database models
from src.config import decode_jwt  # Function to decode JWT tokens
import datetime  # To handle dates
import jwt  # For encoding and decoding JSON Web Tokens (JWT)

# Create a Blueprint for goal-related routes, allowing modular routing
goal_routes = Blueprint('goal_routes', __name__)

# Define a route to set a user's daily goal
@goal_routes.route('/set-goal', methods=['POST'])
def set_goal():
    # Extract the Authorization token from the request headers
    token = request.headers.get('Authorization')

    # Decode the JWT token to extract user information
    data = decode_jwt(token)
    if not data:
        # Return an error response if the token is invalid
        return jsonify({"error": "Invalid token"}), 400

    # Extract the username from the decoded token
    username = data['sub']

    # Query the database to find the user by username
    user = User.query.filter_by(username=username).first()
    if not user:
        # Return an error response if the user does not exist
        return jsonify({"error": "User not found"}), 404

    # Parse the request body to get goal-related data
    goal_data = request.get_json()

    # Create a new goal object for the user
    new_goal = Goal(user_id=user.id, daily_goal_minutes=goal_data.get('daily_goal_minutes'))

    # Add the new goal to the database and commit the changes
    db.session.add(new_goal)
    db.session.commit()

    # Return a success response
    return jsonify({"message": "Daily goal set successfully"}), 200

# Define a route to get the progress of a user's daily goal
@goal_routes.route('/get-goal-progress', methods=['GET'])
def get_goal_progress():
    # Extract the Authorization token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        # Return an error response if the token is missing
        return jsonify({"error": "Token is missing"}), 404

    try:
        # Decode the JWT token to validate it and extract the username
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        username = data['sub']
    except jwt.ExpiredSignatureError:
        # Handle expired token error
        return jsonify({"error": "Token has expired"}), 404
    except jwt.InvalidTokenError:
        # Handle invalid token error
        return jsonify({"error": "Invalid token"}), 404

    # Query the database to find the user by username
    user = User.query.filter_by(username=username).first()

    # Query the database to find the user's goal for the current date
    goal = Goal.query.filter_by(user_id=user.id, date=datetime.date.today()).first()

    if not goal:
        # Return an error response if no goal is set for today
        return jsonify({"error": "No goal set for today"}), 404

    # Query the database to find all workouts for the user on the current date
    workouts_today = Workout.query.filter_by(user_id=user.id).filter(Workout.timestamp >= datetime.date.today()).all()

    # Calculate the total minutes from all workouts today
    total_minutes = sum([workout.duration for workout in workouts_today])

    # Update the achieved_minutes field in the goal
    goal.achieved_minutes = total_minutes
    db.session.commit()

    # Return the user's daily goal and progress as a JSON response
    return jsonify({
        'daily_goal_minutes': goal.daily_goal_minutes,
        'achieved_minutes': goal.achieved_minutes
    }), 200
