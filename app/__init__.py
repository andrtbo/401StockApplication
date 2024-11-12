from flask import Flask

from .extensions import db
from .routes import routes
from .functions import update_stock

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temp_key' #Change key later
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    
    db.init_app(app)
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()
        update_stock()

    return app