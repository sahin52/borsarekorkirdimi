from flask import Flask
from .helper_methods import update_stock_data_in_db
from .models import db
from apscheduler.schedulers.background import BackgroundScheduler  # Corrected import
from dotenv import load_dotenv
import os
import logging

# Load the variables from the .env file
load_dotenv()

# Get the value of the MEMORY variable

class Config:
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_SQLITE_PATH_FOR_DEV_ENV') or 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all() # Create the database tables
    
    # Get the apscheduler logger
    apscheduler_logger = logging.getLogger('apscheduler')
    # Set its level to ERROR
    apscheduler_logger.setLevel(logging.ERROR)
    
    scheduler = BackgroundScheduler()  # Corrected class name
    scheduler.add_job(id='Scheduled task', func=update_stock_data_in_db, args=[app], trigger='interval', seconds=3)
    scheduler.start()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app