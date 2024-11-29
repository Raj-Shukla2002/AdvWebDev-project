from flask import Flask
from src.models.models import db
import os
from src.controllers.user_controller import user_routes
from src.controllers.workout_controller import workout_routes
from src.controllers.goal_controller import goal_routes
from src.controllers.weatherapi_controller import weather_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'fitness_tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)

    app.register_blueprint(user_routes)
    app.register_blueprint(workout_routes)
    app.register_blueprint(goal_routes)
    app.register_blueprint(weather_routes)

    with app.app_context():
        db.create_all()

    return app

app = create_app()
app.run(debug=True)
print(app.app_context())
