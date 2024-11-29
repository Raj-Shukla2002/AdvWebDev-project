from unittest.mock import patch

def test_register_user(test_client):
    
    data = {"username": "test_user", "password": "password123"}
    response = test_client.post('/register', json=data)
    assert response.status_code == 200
    assert response.json["message"] == "User registered successfully"

def test_login_user(test_client):
    
    test_client.post('/register', json={"username": "test_user", "password": "password123"})
    
    response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200
    assert "token" in response.json

    response = test_client.post('/login', json={"username": "test_user", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json["error"] == "Invalid password"

def test_log_workout(test_client):

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

def test_get_workouts(test_client):

    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    
    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.get('/workouts', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json["workouts"], list)

def test_set_goal(test_client):
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

def test_get_goal_progress(test_client):

    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")

    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.get('/get-goal-progress', headers=headers)
    assert response.status_code in [200, 404]

def test_delete_user(test_client):
    
    response = test_client.post('/register', json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200

    login_response = test_client.post('/login', json={"username": "test_user", "password": "password123"})
    assert login_response.status_code == 200
    jwt_token = login_response.json.get("token")
    headers = {"Authorization": f"{jwt_token}"}

    response = test_client.delete('/users/1', headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "User 'test_user' has been deleted successfully"


def test_login_with_github(test_client):

    response = test_client.get('/login-with-github')
    assert response.status_code == 302

@patch('src.controllers.weatherapi_controller.requests.get')
def test_get_weather(mock_requests_get, test_client):

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
