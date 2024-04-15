from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime

db = SQLAlchemy()

class StockData(db.Model):
    __tablename__ = 'StockData'
    data_id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String)
    date = db.Column(DateTime)
    interval = db.Column(db.String)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
