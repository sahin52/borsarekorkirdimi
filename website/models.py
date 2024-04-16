from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime

db = SQLAlchemy()

class StockData(db.Model):
    __tablename__ = 'StockData'
    data_id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String)
    date = db.Column(DateTime)
    interval = db.Column(db.String)
    close = db.Column(db.Float)
    increase_1d = db.Column(db.Float)
    increase_1w = db.Column(db.Float)
    increase_1m = db.Column(db.Float)
    increase_3m = db.Column(db.Float)
    increase_6m = db.Column(db.Float)
    increase_1y = db.Column(db.Float)
    increase_5y = db.Column(db.Float)
    increase_10y = db.Column(db.Float)
    increase_20y = db.Column(db.Float)


