import pytest
from src.app import create_app
from src.models.models import db

# Define a pytest fixture to set up a test client for the Flask application.
@pytest.fixture
def test_client():
    """
    Creates a test client for the Flask application with an in-memory SQLite database.
    This fixture initializes the database, provides a test client for making requests, 
    and cleans up the database after the test is complete.
    """
    # Create the Flask app instance using the application's factory function.
    app = create_app()

    # Configure the app for testing.
    app.config['TESTING'] = True  # Enable testing mode to use Flask's testing utilities.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database.
    app.config['SECRET_KEY'] = 'test_secret_key'  # Set a secret key for JWT or other secure operations.

    # Create a test client for sending HTTP requests to the application.
    with app.test_client() as client:
        # Establish the application context for database operations.
        with app.app_context():
            db.create_all()  # Create all tables defined in the database models.
            yield client  # Yield the test client to the test functions.

            # Clean up after the tests.
            db.session.remove()  # Remove any active database sessions.
            db.drop_all()  # Drop all tables to reset the database state.
