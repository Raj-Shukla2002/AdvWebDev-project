# Import necessary modules
from flask import jsonify, request, Blueprint  # For handling HTTP responses, requests, and route grouping
from src.models.models import db, User, Workout  # Importing the database and models for User and Workout
from src.config import decode_jwt  # Utility to decode JWT tokens
import jwt  # For handling JSON Web Tokens
from flask import current_app  # To access the app's configuration

# Create a Blueprint for workout-related routes
workout_routes = Blueprint('workout_routes', __name__)

# Route to log a workout
@workout_routes.route('/log-workout', methods=['POST'])
def log_workout():
    """
    Log a workout for a user.
    """
    # Get the Authorization token from the request headers
    token = request.headers.get('Authorization')
    data = decode_jwt(token)  # Decode the token to extract user information
    if not data:
        # Return error if the token is invalid
        return jsonify({"error": "Invalid token"}), 400

    # Get the username from the decoded token
    username = data['sub']
    user = User.query.filter_by(username=username).first()  # Fetch the user from the database
    if not user:
        # Return error if the user is not found
        return jsonify({"error": "User not found"}), 404

    # Get workout data from the request body
    workout_data = request.get_json()
    # Create a new workout record
    new_workout = Workout(
        user_id=user.id,  # Associate the workout with the user
        type=workout_data.get('type'),  # Type of workout (e.g., running, swimming)
        category=workout_data.get('category'),  # Category (e.g., cardio, strength)
        duration=workout_data.get('duration'),  # Duration of the workout in minutes
        calories=workout_data.get('calories'),  # Calories burned
    )
    # Add the new workout to the database session
    db.session.add(new_workout)
    db.session.commit()  # Save changes to the database

    # Return success message
    return jsonify({"message": "Workout logged successfully"}), 200

# Route to delete a specific workout
@workout_routes.route('/workout/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """
    Delete a workout by its ID.
    """
    # Get the Authorization token from the request headers
    token = request.headers.get('Authorization')
    data = decode_jwt(token)  # Decode the token to extract user information
    if not data:
        # Return error if the token is invalid
        return jsonify({"error": "Invalid token"}), 400
    
    # Get the username from the decoded token
    username = data['sub']
    user = User.query.filter_by(username=username).first()  # Fetch the user from the database

    # Fetch the workout by its ID
    workout = Workout.query.get(workout_id)
    if not workout:
        # Return error if the workout is not found
        return jsonify({"error": "Workout not found"}), 404

    # Check if the user is authorized to delete this workout
    if user.username != username:
        return jsonify({"error": "You are not authorized to delete this workout"}), 403

    # Delete the workout from the database
    db.session.delete(workout)
    db.session.commit()  # Save changes to the database

    # Return success message
    return jsonify({"message": "Workout deleted successfully"}), 200

# Route to fetch all workouts for the logged-in user
@workout_routes.route('/workouts', methods=['GET'])
def get_workouts():
    """
    Fetch all workouts for the authenticated user.
    """
    # Get the Authorization token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        # Return error if the token is missing
        return jsonify({"error": "Token is missing"}), 404

    try:
        # Decode the token to get user information
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        username = data['sub']
    except jwt.ExpiredSignatureError:
        # Handle expired token error
        return jsonify({"error": "Token has expired"}), 404
    except jwt.InvalidTokenError:
        # Handle invalid token error
        return jsonify({"error": "Invalid token"}), 404

    # Fetch the user from the database
    user = User.query.filter_by(username=username).first()
    # Fetch all workouts associated with the user
    workouts = Workout.query.filter_by(user_id=user.id).all()
    workout_list = []  # Initialize an empty list to store workout details

    # Iterate through the workouts and format the response
    for workout in workouts:
        workout_list.append({
            'type': workout.type,  # Type of workout
            'category': workout.category,  # Workout category
            'duration': workout.duration,  # Duration in minutes
            'calories': workout.calories,  # Calories burned
            'timestamp': workout.timestamp  # Timestamp of when the workout was logged
        })

    # Return the list of workouts
    return jsonify({'workouts': workout_list}), 200
