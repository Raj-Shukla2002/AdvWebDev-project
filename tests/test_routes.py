from unittest.mock import patch

# Test the user registration endpoint
@patch('src.controllers.user_controller.db.session.add')
@patch('src.controllers.user_controller.db.session.commit')
def test_register_user(mock_commit, mock_add, test_client):
    """
    Test the /register endpoint for registering a new user.
    Mocks database add and commit operations to isolate from the actual database.
    """
    data = {"username": "test_user", "password": "password123"}
    response = test_client.post('/register', json=data)
    assert response.status_code == 200
    assert response.json["message"] == "User registered successfully"

# Test the user login endpoint
@patch('src.controllers.user_controller.db.session.add')
@patch('src.controllers.user_controller.db.session.commit')
def test_login_user(mock_commit, mock_add, test_client):
    """
    Test the /login endpoint for authenticating a user.
    Includes both successful and failed login scenarios.
    """
    test_client.post('/register', json={"username": "test_user", "password": "password123"})
    
    response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200
    assert "token" in response.json

    response = test_client.post('/login', json={"username": "test_user", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json["error"] == "Invalid password"

# Test logging a workout
@patch('src.controllers.workout_controller.db.session.add')
@patch('src.controllers.workout_controller.db.session.commit')
def test_log_workout(mock_commit, mock_add, test_client):
    """
    Test the /log-workout endpoint for logging a workout.
    Ensures that the workout is properly recorded in the mocked database.
    """
    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    
    headers = {"Authorization": f"{jwt_token}"}
    data = {
        "type": "Running",
        "category": "Cardio",
        "duration": 30,
        "calories": 200
    }

    response = test_client.post('/log-workout', headers=headers, json=data)
    assert response.status_code == 200
    assert response.json["message"] == "Workout logged successfully"

# Test retrieving logged workouts
@patch('src.controllers.workout_controller.Workout.query.filter_by')
def test_get_workouts(mock_filter_by, test_client):
    """
    Test the /workouts endpoint for fetching all workouts of a user.
    Mocks the database query to return predefined data.
    """
    mock_filter_by.return_value.all.return_value = [
        {"type": "Running", "category": "Cardio", "duration": 30, "calories": 200, "timestamp": "2023-01-01"}
    ]

    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    
    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.get('/workouts', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json["workouts"], list)

# Test setting a daily goal
@patch('src.controllers.goal_controller.db.session.add')
@patch('src.controllers.goal_controller.db.session.commit')
def test_set_goal(mock_commit, mock_add, test_client):
    """
    Test the /set-goal endpoint for setting a daily workout goal.
    Mocks database operations to avoid interacting with the actual database.
    """
    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    headers = {"Authorization": f"{jwt_token}"}
    data = {"daily_goal_minutes": 60}

    response = test_client.post('/set-goal', headers=headers, json=data)
    assert response.status_code == 200
    assert response.json["message"] == "Daily goal set successfully"

# Test fetching goal progress
@patch('src.controllers.goal_controller.Goal.query.filter_by')
def test_get_goal_progress(mock_filter_by, test_client):
    """
    Test the /get-goal-progress endpoint for retrieving the daily goal progress.
    Mocks the goal query to return predefined results or no results.
    """
    mock_filter_by.return_value.first.return_value = None

    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")

    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.get('/get-goal-progress', headers=headers)
    assert response.status_code in [200, 404]

# Test deleting a user
@patch('src.controllers.user_controller.db.session.delete')
@patch('src.controllers.user_controller.db.session.commit')
def test_delete_user(mock_commit, mock_delete, test_client):
    """
    Test the /users/<int:user_id> endpoint for deleting a user.
    Ensures only authorized users can delete their own accounts.
    """
    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.delete('/users/1', headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "User 'test_user' has been deleted successfully"

# Test fetching weather information
@patch('src.controllers.weatherapi_controller.requests.get')
def test_get_weather(mock_requests_get, test_client):
    """
    Test the /weather endpoint for fetching weather information.
    Mocks the requests to the external API for controlled testing scenarios.
    """
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = {
        "main": {"temp": 25},
        "weather": [{"description": "clear sky"}],
        "name": "Test City"
    }

    response = test_client.get('/weather?city=Test City')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["city"] == "Test City"
    assert json_data["temperature"] == 25
    assert json_data["weather"] == "clear sky"
    assert json_data["recommendation"] == "Great weather for outdoor activities like running or cycling."

    response = test_client.get('/weather')
    assert response.status_code == 400
    assert response.get_json() == {"error": "City parameter is required"}

    mock_requests_get.return_value.status_code = 404
    mock_requests_get.return_value.json.return_value = {"message": "city not found"}

    response = test_client.get('/weather?city=Invalid City')
    assert response.status_code == 404
    assert response.get_json() == {"error": {"message": "city not found"}}
