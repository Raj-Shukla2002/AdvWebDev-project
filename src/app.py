# Import necessary modules and libraries
from flask import Flask  # Flask is used to create the application
from src.models.models import db  # Import the database instance from models
import os  # Provides functions to interact with the operating system
from src.controllers.user_controller import user_routes  # Import user routes
from src.controllers.workout_controller import workout_routes  # Import workout routes
from src.controllers.goal_controller import goal_routes  # Import goal routes
from src.controllers.weatherapi_controller import weather_routes  # Import weather API routes

# Function to create and configure the Flask application
def create_app():
    """
    Create and configure the Flask application.
    """
    # Instantiate the Flask app
    app = Flask(__name__)
    
    # Configure the database URI to use SQLite with the file 'fitness_tracker.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'fitness_tracker.db')
    
    # Disable SQLAlchemy modification tracking to save resources
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Set a secret key for session management and security purposes
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize the SQLAlchemy database instance with the app
    db.init_app(app)

    # Register the blueprints for user, workout, goal, and weather-related routes
    app.register_blueprint(user_routes)  # User routes (e.g., login, registration)
    app.register_blueprint(workout_routes)  # Workout-related routes
    app.register_blueprint(goal_routes)  # Goal-related routes
    app.register_blueprint(weather_routes)  # Weather-related routes

    # Create all database tables if they do not already exist
    with app.app_context():  # Ensures the app context is active
        db.create_all()

    # Return the configured Flask app instance
    return app

# Create the Flask application using the `create_app` function
app = create_app()

# Run the app in debug mode (useful for development; should be disabled in production)
app.run(debug=True)

# Print the application context for debugging purposes
print(app.app_context())
