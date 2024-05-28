from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('cred.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


class XU100:
    @staticmethod
    def add(xu100_data):
        db.collection('XU100').add(xu100_data)

class StockData:
    @staticmethod
    def add(stock_data):
        db.collection('StockData').add(stock_data)

    @staticmethod
    def add_all(stocks_data):
        for stock_data in stocks_data:
            StockData.add(stock_data)

class UpdateToDb:
    @staticmethod
    def set_latest_update():
        db.collection('UpdateToDb').document('latest').set({'last_update': datetime.now()})

    @staticmethod
    def get_latest_update():
        return db.collection('UpdateToDb').document('latest').get().to_dict()

class Holidays:
    @staticmethod
    def add(holiday):
        db.collection('Holidays').add(holiday)

    @staticmethod
    def add_all(holidays):
        for holiday in holidays:
            Holidays.add(holiday)

    @staticmethod
    def check_is_holiday(date):
        docs = db.collection('Holidays').where('date', '==', date).stream()
        for doc in docs:
            return doc.to_dict().get('is_holiday', False)
        return False

    @staticmethod
    def does_date_exist(date):
        docs = db.collection('Holidays').where('date', '==', date).stream()
        return any(docs)