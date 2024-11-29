from flask import jsonify, request, Blueprint
from src.models.models import db, User, Workout
from src.config import decode_jwt
import jwt
from flask import current_app

workout_routes = Blueprint('workout_routes', __name__)

@workout_routes.route('/log-workout', methods=['POST'])
def log_workout():
    token = request.headers.get('Authorization')
    data = decode_jwt(token)
    if not data:
        return jsonify({"error": "Invalid token"}), 400

    username = data['sub']
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    workout_data = request.get_json()
    new_workout = Workout(
        user_id=user.id,
        type=workout_data.get('type'),
        category=workout_data.get('category'),
        duration=workout_data.get('duration'),
        calories=workout_data.get('calories'),
    )
    db.session.add(new_workout)
    db.session.commit()

    return jsonify({"message": "Workout logged successfully"}), 200

@workout_routes.route('/workout/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    token = request.headers.get('Authorization')
    data = decode_jwt(token)
    if not data:
        return jsonify({"error": "Invalid token"}), 400
    
    username = data['sub']
    user = User.query.filter_by(username=username).first()

    workout = Workout.query.get(workout_id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    if user.username != username:
        return jsonify({"error": "You are not authorized to delete this workout"}), 403

    db.session.delete(workout)
    db.session.commit()

    return jsonify({"message": "Workout deleted successfully"}), 200

@workout_routes.route('/workouts', methods=['GET'])
def get_workouts():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token is missing"}), 404

    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        username = data['sub']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 404
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 404

    user = User.query.filter_by(username=username).first()
    workouts = Workout.query.filter_by(user_id=user.id).all()
    workout_list = []
    for workout in workouts:
        workout_list.append({
            'type': workout.type,
            'category': workout.category,
            'duration': workout.duration,
            'calories': workout.calories,
            'timestamp': workout.timestamp
        })

    return jsonify({'workouts': workout_list}), 200