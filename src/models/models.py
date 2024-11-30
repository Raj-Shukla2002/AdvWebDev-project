# Import the SQLAlchemy library to handle database operations and models
from flask_sqlalchemy import SQLAlchemy
import datetime  # For handling dates and timestamps

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Define the User model representing users in the system
class User(db.Model):
    """
    Represents a user in the system.
    """
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the user table
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username
    hashed_password = db.Column(db.String(200), nullable=True)  # Encrypted user password
    salt = db.Column(db.String(200), nullable=True)  # Salt used for password hashing

# Define the Workout model representing logged workouts for users
class Workout(db.Model):
    """
    Represents a workout logged by a user.
    """
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the workout table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    # Foreign key linking the workout to a user
    type = db.Column(db.String(80), nullable=False)  # Type of workout (e.g., running, swimming)
    category = db.Column(db.String(80), nullable=False)  # Category of workout (e.g., cardio, strength)
    duration = db.Column(db.Integer, nullable=False)  # Duration of the workout in minutes
    calories = db.Column(db.Integer, nullable=False)  # Calories burned during the workout
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)  
    # Timestamp of when the workout was logged; defaults to the current UTC time

# Define the Goal model representing daily goals set by users
class Goal(db.Model):
    """
    Represents a user's daily fitness goal.
    """
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the goal table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    # Foreign key linking the goal to a user
    daily_goal_minutes = db.Column(db.Integer, nullable=False)  # Number of minutes set as the daily goal
    achieved_minutes = db.Column(db.Integer, default=0)  # Minutes achieved so far for the day
    date = db.Column(db.Date, default=datetime.date.today)  
    # Date for which the goal is set; defaults to the current date
