from flask import jsonify, request, current_app, Blueprint
from src.models.models import db, User, Goal, Workout
from src.config import decode_jwt
import datetime
import jwt

goal_routes = Blueprint('goal_routes', __name__)

@goal_routes.route('/set-goal', methods=['POST'])
def set_goal():
    token = request.headers.get('Authorization')
    data = decode_jwt(token)
    if not data:
        return jsonify({"error": "Invalid token"}), 400

    username = data['sub']
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    goal_data = request.get_json()
    new_goal = Goal(user_id=user.id, daily_goal_minutes=goal_data.get('daily_goal_minutes'))
    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"message": "Daily goal set successfully"}), 200

@goal_routes.route('/get-goal-progress', methods=['GET'])
def get_goal_progress():
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
    goal = Goal.query.filter_by(user_id=user.id, date=datetime.date.today()).first()

    if not goal:
        return jsonify({"error": "No goal set for today"}), 404

    workouts_today = Workout.query.filter_by(user_id=user.id).filter(Workout.timestamp >= datetime.date.today()).all()

    total_minutes = sum([workout.duration for workout in workouts_today])
    goal.achieved_minutes = total_minutes
    db.session.commit()

    return jsonify({
        'daily_goal_minutes': goal.daily_goal_minutes,
        'achieved_minutes': goal.achieved_minutes
    }), 200
