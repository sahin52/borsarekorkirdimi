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
    
    @classmethod
    def add(cls, stock):
        db.session.add(stock)
        db.session.commit()


class Holidays(db.Model):
    __tablename__ = 'Holidays'
    holiday_id = db.Column(db.Integer, primary_key=True)

    # date format: "yyyy-MM-dd"
    date = db.Column(db.String)
    is_holiday = db.Column(db.Boolean)
    
    @classmethod
    def add(cls, holiday):
        db.session.add(holiday)
        db.session.commit()
    
    @classmethod
    def is_holiday(cls, date):
        holiday = Holidays.query.filter(Holidays.date == date).first()
        if holiday:
            return holiday.is_holiday
        return False
    def does_date_exist(cls, date):
        return Holidays.query.filter(Holidays.date == date).first() is not None