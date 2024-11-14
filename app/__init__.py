from flask import Flask
from flask_login import LoginManager

from .extensions import db
from .routes import routes
from .functions import update_stock
from .models import User, MarketHours, LastUpdated

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temp_key' #Change key later
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    
    db.init_app(app)
    app.register_blueprint(routes)

    login_manager = LoginManager()
    login_manager.login_view = 'routes.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        test = MarketHours.query.first()
        if not test:
            init_hours = MarketHours(
                start_time = '5:00 AM',
                end_time = '5:00 PM',
                start_day = 'Monday', 
                end_day =  'Friday'
            )
            init_time = LastUpdated(
                time = '2024-11-12 11:14:07'
            )
            db.session.add(init_hours)
            db.session.add(init_time)
            db.session.commit()

        update_stock()

    return app