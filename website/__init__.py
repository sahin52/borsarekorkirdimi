from flask import Flask
from .helper_methods import update_stock_data_in_db
from .models import db
from apscheduler.schedulers.background import BackgroundScheduler  # Corrected import


class Config:
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all() # Create the database tables
    scheduler = BackgroundScheduler()  # Corrected class name
    scheduler.add_job(id='Scheduled task', func=update_stock_data_in_db, args=[app, False], trigger='interval', minutes=15)
    scheduler.start()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app