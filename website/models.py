from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class XU100(db.Model):
    __tablename__ = 'XU100'
    xu100_id = db.Column(db.Integer, primary_key=True)
    
    latest_update_date = db.Column(db.DateTime)
    latest_price = db.Column(db.Float)
    latest_price_date = db.Column(db.String) # in yyyy-MM-dd format

    last_record = db.Column(db.Float)
    last_record_date = db.Column(db.String)
    todays_highest_price = db.Column(db.Float)

    # date_of_all_time_high_usd = db.Column(db.String)
    # all_time_high_usd = db.Column(db.Float)
    
    @classmethod
    def add(cls, xu100):
        db.session.add(xu100)
        db.session.commit()

class StockData(db.Model):
    __tablename__ = 'StockData'
    data_id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String)
    date = db.Column(db.String) # in yyyy-MM-dd format
    # interval = db.Column(db.String)
    close = db.Column(db.Float)
    increase_1d = db.Column(db.Float)
    increase_1w = db.Column(db.Float)
    increase_1m = db.Column(db.Float)
    increase_3m = db.Column(db.Float)
    increase_6m = db.Column(db.Float)
    increase_1y = db.Column(db.Float)
    increase_5y = db.Column(db.Float)
    
    @classmethod
    def add(cls, stock):
        db.session.add(stock)
        db.session.commit()
    @classmethod
    def add_all(cls, stocks):
        db.session.add_all(stocks)
        db.session.commit()

class UpdateToDb(db.Model):
    data_id = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime)

    @classmethod
    def set_latest_update(cls):
        latest_update = UpdateToDb.query.first()
        if(latest_update is None):
            latest_update = UpdateToDb(last_update = datetime.now())
        db.session.add(latest_update)
        db.session.commit()

    @classmethod
    def get_latest_update(cls):
        return UpdateToDb.query.first()
    

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
    def add_all(cls, holidays):
        db.session.add_all(holidays)
        db.session.commit()
    @classmethod
    def check_is_holiday(cls, date):
        holiday = Holidays.query.filter(Holidays.date == date).first()
        if holiday:
            return holiday.is_holiday
        return False
    @classmethod
    def does_date_exist(cls, date):
        return Holidays.query.filter(Holidays.date == date).first() is not None