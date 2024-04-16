from flask import Flask
from .models import db
from apscheduler.schedulers.background import APScheduler


class Config:
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///..//stock_data.sqlite3'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)  # Add this line
    scheduler = APScheduler()
    scheduler.init_app(app)
    # scheduler.add_job(id='Scheduled task', func=get_historical_stock_data, trigger='interval', seconds=3)
    scheduler.start()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app